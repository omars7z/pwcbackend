import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AuditReport
from groq import Groq

@csrf_exempt
def run_audit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            document = data.get('documentText', '')

            if not document:
                return JsonResponse({'error': 'No document provided.'}, status=400)
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                return JsonResponse({'error': 'GROQ_API_KEY is not configured.'}, status=500)
            client = Groq(api_key=groq_api_key)

            # 1. Instruct the AI on how to behave (The System Prompt)
            system_instruction = (
                "You are 'AssureAgent', an expert AI auditor specializing in Jordanian corporate law and compliance. "
                "Analyze the provided document for regulatory compliance, missing clauses, or financial inconsistencies. "
                "Provide a clear, highly professional summary of your findings. "
                "CRITICAL INSTRUCTION: If violations are found, you must start your response with the exact word 'FAILED:'. "
                "If no violations are found and it looks good, start your response with 'PASSED:'."
            )

            # 2. Call the Groq API (Using LLaMA 3 70B for complex reasoning)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_instruction,
                    },
                    {
                        "role": "user",
                        "content": f"Please audit the following document:\n\n{document}",
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1, # Keep this very low so the AI is factual and analytical, not creative
            )

            raw_ai_response = chat_completion.choices[0].message.content

            # 3. Parse the status dynamically based on the AI's first word
            if "FAILED:" in raw_ai_response.upper():
                status = "Failed Compliance"
            else:
                status = "Passed Compliance"

            # Clean up the FAILED/PASSED tag so it looks pretty in the React frontend
            clean_findings = raw_ai_response.replace("FAILED:", "").replace("PASSED:", "").strip()

            # 4. Save the real AI data to PostgreSQL
            report = AuditReport.objects.create(
                document_text=document,
                compliance_status=status,
                ai_findings=clean_findings
            )

            # 5. Send back to React
            return JsonResponse({
                'status': report.compliance_status,
                'findings': report.ai_findings
            })

        except Exception as e:
            # If the API fails, send the error to the frontend instead of crashing
            return JsonResponse({'error': f"API Error: {str(e)}"}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=405)
from django.db import models

# Create your models here.

class AuditReport(models.Model):
    document_text = models.TextField()
    compliance_status = models.CharField(max_length=50) # 'Passed', 'Failed', 'Review'
    ai_findings = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
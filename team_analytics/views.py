from datetime import date

from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import (
    InjuryStatus,
    Match,
    OpponentProfile,
    Player,
    PlayerMatchStat,
    Position,
    RecommendationSnapshot,
)
from .serializers import MatchInsightSerializer, PlayerDetailSerializer, PlayerMatchStatSerializer, RecommendationSnapshotSerializer


def success_response(data, meta=None):
    return {"success": True, "data": data, "meta": meta or {}, "error": None}


def error_response(code, message, details=None, http_status=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "success": False,
            "data": {},
            "meta": {},
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
                "trace_id": str(timezone.now().timestamp()),
            },
        },
        status=http_status,
    )


@api_view(["GET"])
def dashboard_top_options(request):
    position_code = request.query_params.get("position")
    limit = int(request.query_params.get("limit", 10))
    if not position_code:
        return error_response("VALIDATION_ERROR", "Query param 'position' is required.")

    position = Position.objects.filter(code=position_code).first()
    if not position:
        return error_response("NOT_FOUND", f"Position '{position_code}' does not exist.", http_status=status.HTTP_404_NOT_FOUND)

    snapshots = RecommendationSnapshot.objects.filter(position=position).order_by("-created_at", "-rank_score")[:limit]
    items = RecommendationSnapshotSerializer(snapshots, many=True).data
    page_meta = {"page": 1, "page_size": limit, "total_items": len(items), "total_pages": 1}
    return Response(success_response({"items": items}, meta=page_meta))


@api_view(["GET"])
def dashboard_key_injuries(request):
    injuries = InjuryStatus.objects.filter(is_active=True).select_related("player").order_by("-start_date")[:10]
    data = [
        {
            "player_id": item.player_id,
            "player_name": item.player.name,
            "injury_name": item.injury_name,
            "severity": item.severity,
            "expected_return_date": item.expected_return_date,
        }
        for item in injuries
    ]
    return Response(success_response({"items": data}))


@api_view(["GET"])
def dashboard_replacement_summary(request):
    injured_count = Player.objects.filter(status="INJ").count()
    fit_count = Player.objects.filter(status="FIT").count()
    return Response(
        success_response(
            {
                "injured_count": injured_count,
                "fit_count": fit_count,
                "coverage_health_ratio": round(fit_count / max(injured_count, 1), 2),
            }
        )
    )


@api_view(["GET"])
def dashboard_opponent_summary(request):
    profile = OpponentProfile.objects.order_by("-updated_at").first()
    if not profile:
        return Response(success_response({"opponent": None, "summary": "No opponent profile available."}))

    return Response(
        success_response(
            {
                "opponent": profile.team.name,
                "tactical_style": profile.tactical_style,
                "strengths": profile.strengths,
                "weaknesses": profile.weaknesses,
            }
        )
    )


@api_view(["GET"])
def player_detail(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    serializer = PlayerDetailSerializer(player)
    return Response(success_response(serializer.data))


@api_view(["GET"])
def player_history(request, player_id):
    last_n = int(request.query_params.get("last_n", 10))
    get_object_or_404(Player, pk=player_id)
    stats = PlayerMatchStat.objects.filter(player_id=player_id).select_related("match", "match__away_team").order_by("-match__date")[:last_n]
    serialized = PlayerMatchStatSerializer(stats, many=True).data
    page_meta = {"page": 1, "page_size": last_n, "total_items": len(serialized), "total_pages": 1}
    return Response(success_response({"items": serialized}, meta=page_meta))


@api_view(["GET"])
def match_insights(request, match_id):
    match = get_object_or_404(Match.objects.select_related("away_team"), pk=match_id)
    serializer = MatchInsightSerializer(match)
    lineup_scenarios = [
        {"label": "Balanced 4-2-3-1", "focus": "midfield stability and controlled transitions"},
        {"label": "Aggressive 4-3-3", "focus": "high press and wing overloads"},
    ]
    response_data = serializer.data
    response_data["lineup_scenarios"] = lineup_scenarios
    return Response(success_response(response_data))


@api_view(["GET"])
def admin_overview(request):
    last_snapshot = RecommendationSnapshot.objects.order_by("-created_at").first()
    data = {
        "players_total": Player.objects.count(),
        "active_injuries": InjuryStatus.objects.filter(is_active=True).count(),
        "latest_snapshot_at": last_snapshot.created_at if last_snapshot else None,
        "data_freshness": "healthy" if last_snapshot and (date.today() - last_snapshot.created_at.date()).days <= 1 else "stale",
    }
    return Response(success_response(data))


@api_view(["POST"])
def admin_recompute_recommendations(request):
    position_code = request.data.get("position")
    run_label = request.data.get("run_label", "manual")
    if not position_code:
        return error_response("VALIDATION_ERROR", "Body field 'position' is required.")

    position = Position.objects.filter(code=position_code).first()
    if not position:
        return error_response("NOT_FOUND", f"Position '{position_code}' does not exist.", http_status=status.HTTP_404_NOT_FOUND)

    candidates = (
        Player.objects.filter(primary_position=position, status="FIT")
        .annotate(position_rank_score=(F("overall_rating") * 0.5) + (F("recent_form_index") * 0.3) + (F("fitness_score") * 0.2))
        .order_by("-position_rank_score")[:10]
    )

    created = 0
    for player in candidates:
        RecommendationSnapshot.objects.create(
            position=position,
            player=player,
            rank_score=round(float(player.position_rank_score), 2),
            confidence=round(min(max(float(player.fitness_score) / 100, 0.1), 0.99), 2),
            why_recommended=["High recent form", "Position fit", "Fitness available"],
            risk_flags=["Minor injury risk"] if player.fitness_score < 70 else [],
            run_label=run_label,
        )
        created += 1

    return Response(success_response({"created_snapshots": created, "run_label": run_label}), status=status.HTTP_201_CREATED)
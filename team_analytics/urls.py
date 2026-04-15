from django.urls import path

from .views import (
    admin_overview,
    admin_recompute_recommendations,
    dashboard_key_injuries,
    dashboard_opponent_summary,
    dashboard_replacement_summary,
    dashboard_top_options,
    match_insights,
    player_detail,
    player_history,
)

urlpatterns = [
    path("dashboard/top-options", dashboard_top_options),
    path("dashboard/key-injuries", dashboard_key_injuries),
    path("dashboard/replacement-summary", dashboard_replacement_summary),
    path("dashboard/opponent-summary", dashboard_opponent_summary),
    path("players/<int:player_id>", player_detail),
    path("players/<int:player_id>/history", player_history),
    path("matches/<int:match_id>/insights", match_insights),
    path("admin/overview", admin_overview),
    path("admin/recommendations/recompute", admin_recompute_recommendations),
]
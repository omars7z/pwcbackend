from django.contrib import admin

from .models import (
    AvailabilityWindow,
    Club,
    Competition,
    InjuryStatus,
    Match,
    MatchEvent,
    MatchLineup,
    OpponentProfile,
    Player,
    PlayerMatchStat,
    Position,
    RecommendationSnapshot,
    Season,
    Team,
)

admin.site.register(Team)
admin.site.register(Club)
admin.site.register(Position)
admin.site.register(Player)
admin.site.register(Competition)
admin.site.register(Season)
admin.site.register(Match)
admin.site.register(MatchLineup)
admin.site.register(MatchEvent)
admin.site.register(PlayerMatchStat)
admin.site.register(InjuryStatus)
admin.site.register(AvailabilityWindow)
admin.site.register(OpponentProfile)
admin.site.register(RecommendationSnapshot)

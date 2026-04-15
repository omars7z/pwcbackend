from rest_framework import serializers

from .models import Match, OpponentProfile, Player, PlayerMatchStat, RecommendationSnapshot


class PlayerMatchStatSerializer(serializers.ModelSerializer):
    opponent = serializers.SerializerMethodField()
    match_date = serializers.DateField(source="match.date", read_only=True)

    class Meta:
        model = PlayerMatchStat
        fields = [
            "id",
            "match_date",
            "opponent",
            "minutes_played",
            "distance_covered_km",
            "pass_accuracy_percent",
            "rating",
            "goals",
            "assists",
        ]

    def get_opponent(self, obj):
        return obj.match.away_team.name


class PlayerDetailSerializer(serializers.ModelSerializer):
    primary_position = serializers.CharField(source="primary_position.code", default=None)
    season_summary = serializers.SerializerMethodField()
    strengths = serializers.SerializerMethodField()
    suitability_score = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            "id",
            "name",
            "status",
            "primary_position",
            "overall_rating",
            "recent_form_index",
            "fitness_score",
            "minutes_last_5",
            "goal_contribution_rate",
            "season_summary",
            "strengths",
            "suitability_score",
        ]

    def get_season_summary(self, obj):
        return {
            "minutes_last_5": obj.minutes_last_5,
            "goal_contribution_rate": float(obj.goal_contribution_rate),
        }

    def get_strengths(self, obj):
        strength_list = []
        if obj.passing >= 70:
            strength_list.append("Strong passing")
        if obj.stamina >= 70:
            strength_list.append("High stamina")
        if obj.pace >= 70:
            strength_list.append("Good pace")
        return strength_list or ["Balanced profile"]

    def get_suitability_score(self, obj):
        return round((obj.overall_rating * 0.5) + (float(obj.recent_form_index) * 0.3) + (float(obj.fitness_score) * 0.2), 2)


class RecommendationSnapshotSerializer(serializers.ModelSerializer):
    player_id = serializers.IntegerField(source="player.id")
    player_name = serializers.CharField(source="player.name")
    position = serializers.CharField(source="position.code")

    class Meta:
        model = RecommendationSnapshot
        fields = [
            "player_id",
            "player_name",
            "position",
            "rank_score",
            "confidence",
            "why_recommended",
            "risk_flags",
        ]


class OpponentProfileSerializer(serializers.ModelSerializer):
    opponent = serializers.CharField(source="team.name")

    class Meta:
        model = OpponentProfile
        fields = ["opponent", "tactical_style", "strengths", "weaknesses", "updated_at"]


class MatchInsightSerializer(serializers.ModelSerializer):
    opponent = serializers.CharField(source="away_team.name")
    tactical_strengths = serializers.SerializerMethodField()
    tactical_weaknesses = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ["id", "date", "opponent", "goals_for", "goals_against", "tactical_strengths", "tactical_weaknesses"]

    def get_tactical_strengths(self, obj):
        profile = OpponentProfile.objects.filter(team=obj.away_team).order_by("-updated_at").first()
        return profile.strengths if profile else []

    def get_tactical_weaknesses(self, obj):
        profile = OpponentProfile.objects.filter(team=obj.away_team).order_by("-updated_at").first()
        return profile.weaknesses if profile else []
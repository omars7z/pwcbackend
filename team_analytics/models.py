from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fifa_code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=120, unique=True)
    country = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    code = models.CharField(max_length=5, unique=True)  # ST, RW, CM, ...
    label = models.CharField(max_length=40)

    def __str__(self):
        return self.code


class Player(models.Model):
    STATUS_CHOICES = [
        ("FIT", "Match Fit"),
        ("INJ", "Injured"),
        ("SUS", "Suspended"),
    ]

    name = models.CharField(max_length=120)
    team = models.ForeignKey(Team, related_name="players", on_delete=models.CASCADE)
    current_club = models.ForeignKey(
        Club,
        related_name="players",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    primary_position = models.ForeignKey(
        Position,
        related_name="primary_players",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    secondary_positions = models.ManyToManyField(Position, blank=True, related_name="secondary_players")
    is_local_league = models.BooleanField(default=False)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default="FIT")
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    pace = models.IntegerField(default=50)
    passing = models.IntegerField(default=50)
    stamina = models.IntegerField(default=50)
    recent_form_index = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    fitness_score = models.DecimalField(max_digits=5, decimal_places=2, default=50)
    minutes_last_5 = models.IntegerField(default=0)
    goal_contribution_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.primary_position.code if self.primary_position else 'NA'})"


class Competition(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Season(models.Model):
    label = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.label


class Match(models.Model):
    competition = models.ForeignKey(
        Competition, related_name="matches", on_delete=models.SET_NULL, null=True, blank=True
    )
    season = models.ForeignKey(Season, related_name="matches", on_delete=models.SET_NULL, null=True, blank=True)
    home_team = models.ForeignKey(Team, related_name="home_matches", on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name="away_matches", on_delete=models.CASCADE)
    date = models.DateField()
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date}"


class MatchLineup(models.Model):
    match = models.ForeignKey(Match, related_name="lineups", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="lineups", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, related_name="lineups", on_delete=models.SET_NULL, null=True)
    is_starting = models.BooleanField(default=True)

    class Meta:
        unique_together = ("match", "player")


class MatchEvent(models.Model):
    EVENT_CHOICES = [
        ("GOAL", "Goal"),
        ("ASSIST", "Assist"),
        ("CARD", "Card"),
        ("INJ", "Injury"),
        ("SUB", "Substitution"),
    ]
    match = models.ForeignKey(Match, related_name="events", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="events", on_delete=models.SET_NULL, null=True, blank=True)
    minute = models.PositiveIntegerField(default=0)
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)
    details = models.JSONField(default=dict, blank=True)


class PlayerMatchStat(models.Model):
    player = models.ForeignKey(Player, related_name="performances", on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name="player_stats", on_delete=models.CASCADE)
    minutes_played = models.IntegerField(default=0)
    distance_covered_km = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    pass_accuracy_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=6.0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("player", "match")


class InjuryStatus(models.Model):
    player = models.ForeignKey(Player, related_name="injuries", on_delete=models.CASCADE)
    injury_name = models.CharField(max_length=120)
    severity = models.CharField(max_length=30, default="moderate")
    start_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class AvailabilityWindow(models.Model):
    player = models.ForeignKey(Player, related_name="availability_windows", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=120, blank=True)


class OpponentProfile(models.Model):
    team = models.ForeignKey(Team, related_name="opponent_profiles", on_delete=models.CASCADE)
    tactical_style = models.CharField(max_length=120)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class RecommendationSnapshot(models.Model):
    position = models.ForeignKey(Position, related_name="snapshots", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="recommendation_snapshots", on_delete=models.CASCADE)
    rank_score = models.DecimalField(max_digits=6, decimal_places=2)
    confidence = models.DecimalField(max_digits=4, decimal_places=2, default=0.5)
    why_recommended = models.JSONField(default=list, blank=True)
    risk_flags = models.JSONField(default=list, blank=True)
    run_label = models.CharField(max_length=60, default="manual")
    created_at = models.DateTimeField(auto_now_add=True)
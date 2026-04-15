from datetime import date, timedelta

from django.core.management.base import BaseCommand

from team_analytics.models import (
    Club,
    Competition,
    InjuryStatus,
    Match,
    OpponentProfile,
    Player,
    PlayerMatchStat,
    Position,
    RecommendationSnapshot,
    Season,
    Team,
)


class Command(BaseCommand):
    help = "Reset and seed demo dataset for Jordan WC 2026 MVP."

    def handle(self, *args, **kwargs):
        self.stdout.write("Resetting demo data...")
        RecommendationSnapshot.objects.all().delete()
        InjuryStatus.objects.all().delete()
        PlayerMatchStat.objects.all().delete()
        Match.objects.all().delete()
        OpponentProfile.objects.all().delete()
        Player.objects.all().delete()
        Position.objects.all().delete()
        Club.objects.all().delete()
        Competition.objects.all().delete()
        Season.objects.all().delete()
        Team.objects.all().delete()

        jordan = Team.objects.create(name="Jordan", fifa_code="JOR")
        spain = Team.objects.create(name="Spain", fifa_code="ESP")
        morocco = Team.objects.create(name="Morocco", fifa_code="MAR")

        st = Position.objects.create(code="ST", label="Striker")
        rw = Position.objects.create(code="RW", label="Right Winger")
        cm = Position.objects.create(code="CM", label="Central Midfielder")

        club1 = Club.objects.create(name="Al Wehdat", country="Jordan")
        club2 = Club.objects.create(name="Real Betis", country="Spain")
        club3 = Club.objects.create(name="Wydad", country="Morocco")

        season = Season.objects.create(
            label="2025/26",
            start_date=date(2025, 8, 1),
            end_date=date(2026, 6, 30),
        )
        competition = Competition.objects.create(name="World Cup Qualifier")

        p1 = Player.objects.create(
            name="Yazan Al Naimat",
            team=jordan,
            current_club=club1,
            primary_position=st,
            status="INJ",
            overall_rating=82,
            pace=79,
            passing=67,
            stamina=72,
            recent_form_index=78,
            fitness_score=58,
            minutes_last_5=342,
            goal_contribution_rate=0.61,
        )
        p2 = Player.objects.create(
            name="Mahmoud Al Mardi",
            team=jordan,
            current_club=club2,
            primary_position=rw,
            status="FIT",
            overall_rating=79,
            pace=81,
            passing=73,
            stamina=75,
            recent_form_index=76,
            fitness_score=84,
            minutes_last_5=390,
            goal_contribution_rate=0.48,
        )
        p3 = Player.objects.create(
            name="Nizar Al Rashdan",
            team=jordan,
            current_club=club3,
            primary_position=cm,
            status="FIT",
            overall_rating=77,
            pace=64,
            passing=78,
            stamina=80,
            recent_form_index=74,
            fitness_score=87,
            minutes_last_5=410,
            goal_contribution_rate=0.36,
        )
        p4 = Player.objects.create(
            name="Ali Olwan",
            team=jordan,
            current_club=club1,
            primary_position=st,
            status="FIT",
            overall_rating=80,
            pace=77,
            passing=69,
            stamina=74,
            recent_form_index=80,
            fitness_score=86,
            minutes_last_5=395,
            goal_contribution_rate=0.52,
        )

        InjuryStatus.objects.create(
            player=p1,
            injury_name="Hamstring strain",
            severity="moderate",
            start_date=date.today() - timedelta(days=3),
            expected_return_date=date.today() + timedelta(days=12),
            is_active=True,
        )

        match = Match.objects.create(
            competition=competition,
            season=season,
            home_team=jordan,
            away_team=spain,
            date=date.today() - timedelta(days=7),
            goals_for=1,
            goals_against=2,
        )
        PlayerMatchStat.objects.create(player=p2, match=match, minutes_played=90, distance_covered_km=10.40, pass_accuracy_percent=82.1, rating=7.4, goals=1, assists=0)
        PlayerMatchStat.objects.create(player=p3, match=match, minutes_played=90, distance_covered_km=11.10, pass_accuracy_percent=86.7, rating=7.2, goals=0, assists=1)
        PlayerMatchStat.objects.create(player=p4, match=match, minutes_played=76, distance_covered_km=8.90, pass_accuracy_percent=78.3, rating=7.0, goals=0, assists=0)

        OpponentProfile.objects.create(
            team=morocco,
            tactical_style="High press with compact midfield block",
            strengths=["Ball recovery in middle third", "Fast wing transitions"],
            weaknesses=["Space behind fullbacks", "Set-piece second-ball coverage"],
        )

        RecommendationSnapshot.objects.create(
            position=st,
            player=p4,
            rank_score=86.4,
            confidence=0.81,
            why_recommended=["High recent form", "Strong off-ball movement"],
            risk_flags=[],
            run_label="seed",
        )

        self.stdout.write(self.style.SUCCESS("Demo dataset reset complete."))

from django.test import TestCase
from django.contrib import auth
from faker import Faker

from match.models import Match, Leg, Turn
from player.models import League, Player


User = auth.get_user_model()


class MatchTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.league = League.objects.create(
            name=self.fake.word()
        )
        for _ in range(3):
            user = User.objects.create(
                username=self.fake.user_name(),
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                email=self.fake.email()
            )
            player = Player.objects.create(
                user=user
            )
            self.league.players.add(player)
        self.match = Match.objects.create(
            player1=Player.objects.first(),
            player2=Player.objects.last(),
            league=self.league
        )
        self.leg = Leg.objects.create(
            match=self.match
        )
        self.turn = Turn.objects.create(
            leg=self.leg,
            player=self.match.player1,
        )

    # Model Tests
    def test_match_str(self):
        self.assertEqual(
            self.match.__str__(),
            f'{self.match.timestamp} {self.match.typus}: {self.match.player1} - {self.match.player2}'
        )

    def test_leg_str(self):
        self.assertEqual(
            self.leg.__str__(),
            f'{self.leg.match} Leg {self.leg.ord}'
        )

    def test_turn_str(self):
        self.assertEqual(
            self.turn.__str__(),
            f'{self.turn.leg} {self.turn.player}'
        )

    # Form Tests
    def test_match_form(self):
        pass

    # View Tests
    def test_match_create_view(self):
        pass

    def test_board_view(self):
        pass

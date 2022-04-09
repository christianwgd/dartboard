from django.test import TestCase
from django.contrib import auth
from faker import Faker

from player.models import League, Player


User = auth.get_user_model()


class PlayerTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.league = League.objects.create(
            name=self.fake.word()
        )
        user = User.objects.create(
            username=self.fake.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            email=self.fake.email()
        )
        self.player = Player.objects.create(
            user=user
        )
        self.league.players.add(self.player)

    # Model Tests
    def test_player_str(self):
        self.assertEqual(self.player.__str__(), self.player.user.username)
        self.player.nickname = self.fake.word()
        self.player.save()
        self.player.refresh_from_db()
        self.assertEqual(self.player.__str__(), self.player.nickname)

    def test_league_str(self):
        self.assertEqual(self.league.__str__(), self.league.name)

    # Form Tests
    def test_player_form(self):
        pass

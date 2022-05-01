from django.test import TestCase
from django.contrib import auth
from django.utils.translation import gettext as _
from faker import Faker

from player.forms import PlayerForm
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
    def test_player_form_valid(self):
        form_data = {
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'email': self.fake.email(),
            'nickname': self.fake.word(),
        }
        form = PlayerForm(form_data)
        self.assertTrue(form.is_valid())

    def test_player_form_invalid(self):
        form_data = {
            'email': self.fake.word(),
        }
        form = PlayerForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['email'], [_('Enter a valid email address.')])

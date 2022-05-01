from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils.translation import gettext as _
from faker import Faker

from player.forms import PlayerForm, UserForm, LeagueForm
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

    def test_user_form_valid(self):
        form_data = {
            'username': self.fake.user_name(),
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'email': self.fake.email(),
            'nickname': self.fake.word(),
        }
        form = UserForm(form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid(self):
        form_data = {}
        form = UserForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['username'], [_('This field is required.')])

    def test_league_form_valid(self):
        form_data = {
            'name': self.fake.word(),
        }
        form = LeagueForm(form_data)
        self.assertTrue(form.is_valid())

    def test_league_form_invalid(self):
        form_data = {}
        form = LeagueForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['name'], [_('This field is required.')])

    # Views test
    def test_league_create_view(self):
        url = reverse('player:create', kwargs={'league_id': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_match_create_view(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('player:create', kwargs={'league_id': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        username = self.fake.user_name()
        nickname = self.fake.word()
        form_data = {
            'username': username,
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'email': self.fake.email(),
            'nickname': nickname,
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('player:league-list'))
        user = User.objects.get(username=username)
        self.assertTrue(hasattr(user, 'player'))
        self.assertEqual(user.player.nickname, nickname)

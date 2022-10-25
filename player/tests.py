from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils.translation import gettext as _
from faker import Faker

from player.forms import PlayerForm, UserForm, LeagueForm, PlayerSelectForm
from player.models import League, Player


User = auth.get_user_model()


class PlayerTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.league = League.objects.create(
            name=self.fake.word()
        )
        self.user = User.objects.create(
            username=self.fake.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            email=self.fake.email()
        )
        self.player = Player.objects.create(
            user=self.user,
        )
        self.league.players.add(self.player)
        self.league.managers.add(self.player)

    # Model Tests
    def test_player_str(self):
        self.assertEqual(str(self.player), self.player.user.username)
        self.player.nickname = self.fake.word()
        self.player.save()
        self.player.refresh_from_db()
        self.assertEqual(str(self.player), self.player.nickname)

    def test_league_str(self):
        self.assertEqual(str(self.league), self.league.name)

    # Form Tests
    def test_player_form_valid(self):
        form_data = {
            'username': self.fake.user_name(),
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

    def test_player_select_form_valid(self):
        player = Player.objects.first()
        form_data = {
            'players': [player.id],
        }
        form = PlayerSelectForm(form_data)
        self.assertTrue(form.is_valid())

    def test_player_select_form_invalid(self):
        form_data = {
            'players': [5],
        }
        form = PlayerSelectForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)

    # Views test
    def test_user_create_view_no_auth(self):
        url = reverse('player:create', kwargs={'league_id': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_user_create_view(self):
        self.client.force_login(self.user)
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

    def test_player_update_view_no_auth(self):
        url = reverse('player:update')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_player_update_view(self):
        self.client.force_login(self.user)
        url = reverse('player:update')
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
        self.assertEqual(response.url, reverse('home'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, username)
        self.assertTrue(hasattr(self.user, 'player'))
        self.assertEqual(self.user.player.nickname, nickname)

    def test_league_list_view_no_auth(self):
        url = reverse('player:league-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_league_list_view(self):
        self.client.force_login(self.user)
        url = reverse('player:league-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['league_list']), 1)

    def test_league_create_view_no_auth(self):
        url = reverse('player:league-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_league_create_view(self):
        self.client.force_login(self.user)
        url = reverse('player:league-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        name = self.fake.word()
        response = self.client.post(url, {'name': name})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('player:league-list'))
        self.assertEqual(League.objects.count(), 2)
        new_league = League.objects.get(name=name)
        self.assertEqual(new_league.name, name)
        self.assertEqual(new_league.players.count(), 0)
        self.assertEqual(new_league.managers.count(), 1)
        self.assertEqual(new_league.managers.first(), self.user.player)

    def test_league_update_view_no_auth(self):
        url = reverse('player:league-update', kwargs={'pk': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_league_update_view(self):
        self.client.force_login(self.user)
        url = reverse('player:league-update', kwargs={'pk': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        name = self.fake.word()
        response = self.client.post(url, {'name': name})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('player:league-list'))
        self.league.refresh_from_db()
        self.assertEqual(self.league.name, name)

    def test_player_add_to_league_view_no_auth(self):
        url = reverse('player:add-to-league', kwargs={'pk': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_player_add_to_league_view(self):
        new_user = User.objects.create(
            username=self.fake.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            email=self.fake.email()
        )
        new_player = Player.objects.create(
            user=new_user,
        )
        self.assertEqual(self.league.players.count(), 1)
        self.client.force_login(self.user)
        url = reverse('player:add-to-league', kwargs={'pk': self.league.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form_data = {
            'players': [self.player.id, new_player.id],
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('player:league-list'))
        self.assertEqual(self.league.players.count(), 2)

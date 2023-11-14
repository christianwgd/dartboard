import pytest
from django.conf import settings
from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _
from faker import Faker

from match.forms import MatchForm
from match.models import Match, Leg, Turn
from player.models import League, Player


User = auth.get_user_model()


class MatchTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.league = League.objects.create(
            name=self.fake.word(),
        )
        for _i in range(3):
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
        self.league.managers.add(Player.objects.first())
        self.match = Match.objects.create(
            player1=Player.objects.first(),
            player2=Player.objects.last(),
            league=self.league,
            score_player1=275,
            score_player2=301,
            typus='301'
        )
        self.leg = Leg.objects.create(
            match=self.match
        )
        self.turn = Turn.objects.create(
            leg=self.leg,
            player=self.match.player1,
            throw1=1,
            throw2=20,
            throw3=5,
        )

    # Model Tests
    def test_match_str(self):
        tmstmp = formats.date_format(
            timezone.localtime(self.match.timestamp),
            'SHORT_DATETIME_FORMAT'
        )
        self.assertEqual(
            str(self.match),
            f'{self.match.typus}: {self.match.player1} - {self.match.player2} ({tmstmp})'
        )

    def test_leg_str(self):
        self.assertEqual(
            str(self.leg),
            f'{self.leg.match} Leg {self.leg.ord}'
        )

    def test_turn_str(self):
        self.assertEqual(
            str(self.turn),
            f'{self.turn.leg} {self.turn.player}'
        )

    # Form Tests
    def test_match_form_valid(self):
        player1 = Player.objects.first()
        player2 = Player.objects.last()
        form_data = {
            'league': self.league,
            'first_to': 3,
            'typus': '501',
            'out': 'DO',
            'player1': player1,
            'player2': player2
        }
        form = MatchForm(form_data)
        self.assertTrue(form.is_valid())

    def test_match_form_invalid_same_players(self):
        player1 = Player.objects.first()
        player2 = player1
        form_data = {
            'league': self.league,
            'first_to': 3,
            'typus': '501',
            'out': 'DO',
            'player1': player1,
            'player2': player2
        }
        form = MatchForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn(
            _('Player 2 cannot be the same as player 1'),
            form.errors['player2']
        )

    def test_match_form_invalid_empty(self):
        form_data = {}
        form = MatchForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)

    # View Tests
    def test_match_create_view_no_auth(self):
        url = reverse('match:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_match_create_view(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['unfinished']), 1)
        player1 = Player.objects.first()
        player2 = Player.objects.last()
        form_data = {
            'league': self.league.id,
            'first_to': 3,
            'typus': '501',
            'out': 'DO',
            'player1': player1.id,
            'player2': player2.id
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        new_match = Match.objects.latest('timestamp')
        self.assertEqual(response.url, reverse('match:board', kwargs={'pk': new_match.id}))

    def test_match_board_view_no_auth(self):
        url = reverse('match:board', kwargs={'pk': self.match.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_match_board_view(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:board', kwargs={'pk': self.match.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['match'], self.match)
        self.assertEqual(response.context['multipliers'], [1, 2, 3])
        self.assertEqual(response.context['fields'], range(1, 21))
        self.assertEqual(response.context['p1_latest_score'], 26)
        self.assertEqual(response.context['p1_old_score'], 301)
        self.assertEqual(response.context['active'], 'player1')

    def test_match_summary_view_no_auth(self):
        url = reverse('match:summary', kwargs={'pk': self.match.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_match_summary_view(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:summary', kwargs={'pk': self.match.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['match'], self.match)
        # Check staticstics...

    def test_match_delete_view_no_auth(self):
        url = reverse('match:delete', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_match_delete_view(self):
        match = Match.objects.create(
            player1=Player.objects.first(),
            player2=Player.objects.last(),
            league=self.league,
            score_player1=475,
        )
        user = User.objects.first()
        self.client.force_login(user)
        match_id = match.id
        url = reverse('match:delete', kwargs={'match_id': match_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('match:create'))
        with pytest.raises(Match.DoesNotExist):
            Match.objects.get(pk=match_id)

    def test_get_checkout_view_no_auth(self):
        url = reverse('match:checkout', kwargs={'remaining': 119})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_get_checkout_view(self):
        checkout_url = getattr(settings, 'CHECKOUT_URL', None)
        if checkout_url is not None:
            user = User.objects.first()
            self.client.force_login(user)
            url = reverse('match:checkout', kwargs={'remaining': 119})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(
                response.content,
                '{"darts":'
                '    ['
                '       {"field": 19, "region": "Triple"}, '
                '       {"field": 12, "region": "Triple"}, '
                '       {"field": 13, "region": "Double"}'
                '   ]'
                '}'
            )

    def test_save_turn_view_no_auth(self):
        url = reverse('match:save_turn', kwargs={'match_id': self.match.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"{reverse('login')}?next={url}")

    def test_save_turn_view_no_player(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:save_turn', kwargs={'match_id': self.match.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "reason": "No player provided"}
        )

    def test_save_turn_view_player_not_exists(self):
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:save_turn', kwargs={'match_id': self.match.id})
        response = self.client.post(
            url,
            'player=9',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "reason": "Player does not exist"}
        )

    def test_save_turn_view_player_not_in_match(self):
        user = User.objects.create(
            username=self.fake.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            email=self.fake.email()
        )
        player_not_in_match = Player.objects.create(
            user=user
        )
        user = User.objects.first()
        self.client.force_login(user)
        url = reverse('match:save_turn', kwargs={'match_id': self.match.id})
        response = self.client.post(
            url,
            f'player={player_not_in_match.id}',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "reason": "Player is not in match"}
        )

    def test_save_turn_view_success(self):
        user = User.objects.first()
        self.client.force_login(user)
        old_score = self.match.score_player2
        url = reverse('match:save_turn', kwargs={'match_id': self.match.id})
        response = self.client.post(
            url,
            f'player={self.match.player2.id}&throw1={1}&throw2={5}&throw3={20}&won=false',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.score_player2, old_score-26)
        new_turn = Turn.objects.latest('ord')
        self.assertEqual(new_turn.leg, self.turn.leg)
        self.assertEqual(new_turn.player, self.match.player2)
        self.assertEqual(new_turn.ord, self.turn.ord + 1)
        self.assertEqual(new_turn.throw1, 1)
        self.assertEqual(new_turn.throw2, 5)
        self.assertEqual(new_turn.throw3, 20)
        self.assertJSONEqual(
            response.content,
            {
                "next_player": 1, "old_score": old_score,
                "success": True, "throw_score": 26, "match_finished": False,
            }
        )

    def test_save_turn_view_won(self):
        user = User.objects.first()
        self.client.force_login(user)

        self.assertEqual(self.match.score_player1, 275)
        self.assertEqual(self.match.score_player2, 301)

        url = reverse('match:save_turn', kwargs={'match_id': self.match.id})

        response = self.client.post(
            url,
            f'player={self.match.player2.id}&throw1={1}&throw2={60}&throw3={60}&won=false',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.score_player2, 180)

        response = self.client.post(
            url,
            f'player={self.match.player1.id}&throw1={25}&throw2={50}&throw3={50}&won=false',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.score_player1, 150)

        response = self.client.post(
            url,
            f'player={self.match.player2.id}&throw1={60}&throw2={40}&throw3={20}&won=false',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.score_player2, 60)

        response = self.client.post(
            url,
            f'player={self.match.player1.id}&throw1={50}&throw2={50}&throw3={50}&won=true',
            content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, 200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.score_player1, 301)
        self.assertEqual(self.match.score_player2, 301)

        self.leg.refresh_from_db()
        self.assertEqual(self.leg.winner, self.match.player1)
        new_turn = Turn.objects.latest('ord')
        self.assertEqual(new_turn.leg, self.turn.leg)
        self.assertEqual(new_turn.player, self.match.player1)
        self.assertEqual(self.leg.turns.count(), 5)
        self.assertEqual(new_turn.ord, 5)
        self.assertEqual(new_turn.throw1, 50)
        self.assertEqual(new_turn.throw2, 50)
        self.assertEqual(new_turn.throw3, 50)
        self.assertJSONEqual(
            response.content,
            {
                "next_player": 2, "old_score": 0,
                "success": True, "throw_score": 0, "match_finished": False,
            }
        )

    def test_save_turn_view_bust(self):
        pass

    def test_save_turn_end_game(self):
        pass

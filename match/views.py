import sys

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView

from match.forms import MatchForm
from match.models import Match, Turn, Leg
from player.models import Player


class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchForm

    def get_success_url(self):
        return reverse('match:board', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['unfinished'] = Match.objects.filter(
            league__in=self.request.user.player.leagues.all(),
            winner=None,
        )[:3]
        return ctx

    def form_valid(self, form):
        match = form.save(commit=True)
        Leg.objects.create(match=match)
        initial_score = int(match.typus)
        match.score_player1 = initial_score
        match.score_player2 = initial_score
        return super().form_valid(form)


class MatchBoardView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'match/match_board.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['multipliers'] = [1, 2, 3]
        ctx['fields'] = range(1, 21)
        leg = self.object.legs.latest('ord')
        try:
            p1_turn = leg.turns.filter(player=self.object.player1).latest('ord')
            ctx['p1_latest_score'] = p1_turn.throw1 + p1_turn.throw2 + p1_turn.throw3
            ctx['p1_old_score'] = self.object.score_player1 + ctx['p1_latest_score']
        except Turn.DoesNotExist:
            pass
        try:
            p2_turn = leg.turns.filter(player=self.object.player2).latest('ord')
            ctx['p2_latest_score'] = p2_turn.throw1 + p2_turn.throw2 + p2_turn.throw3
            ctx['p2_old_score'] = self.object.score_player2 + ctx['p2_latest_score']
        except Turn.DoesNotExist:
            pass
        active_player = (leg.ord % 2)
        if active_player == 0:
            ctx['active'] = 'player2'
        else:
            ctx['active'] = 'player1'
        return ctx


class MatchSummaryView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'match/match_summary.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        legs = Leg.objects.filter(match_id=self.object.id)
        turns = Turn.objects.filter(leg__in=legs)
        p1_turs = turns.filter(player_id=self.object.player1)
        p2_turs = turns.filter(player_id=self.object.player2)
        if p1_turs:
            ctx["player1_average"] = sum(turn.score() for turn in p1_turs) / len(p1_turs)
        else:
            ctx["player1_average"] = 0
        if p2_turs:
            ctx["player2_average"] = sum(turn.score() for turn in p2_turs) / len(p2_turs)
        else:
            ctx["player2_average"] = 0
        ctx["player1_legs"] = len(legs.filter(winner=self.object.player1))
        ctx["player2_legs"] = len(legs.filter(winner=self.object.player2))
        return ctx


@login_required
def delete_match(request, match_id):
    Match.objects.get(pk=match_id).delete()
    return redirect(reverse('match:create'))


@login_required
@require_http_methods(["POST"])
def save_turn(request, match_id):
    player_id = request.POST.get('player', None)
    won = request.POST.get('won', 'false') == 'true'
    if not player_id:
        return JsonResponse(
            {'success': False, 'reason': 'No player provided'},
            safe=False
        )
    try:
        player = Player.objects.get(pk=player_id)
    except Player.DoesNotExist:
        return JsonResponse(
            {'success': False, 'reason': 'Player does not exist'},
            safe=False
        )
    throws = [int(request.POST.get(f'throw{i}', 0)) for i in range(1, 4)]
    throw_score = sum(throws)
    match = Match.objects.get(pk=match_id)
    leg = match.legs.last()
    ordinal = leg.turns.count() + 1
    Turn.objects.create(
        leg=leg,
        player=player,
        ord=ordinal,
        throw1=throws[0],
        throw2=throws[1],
        throw3=throws[2],
    )
    if won:
        leg.winner = player
        leg.save()
        match_finished = max(len(match.legs.filter(winner_id=match.player1.id)), len(match.legs.filter(winner_id=match.player1.id))) == match.best_of
        new_ord = leg.ord + 1
        Leg.objects.create(match=match, ord=new_ord)
        throw_score = 0
        old_score = 0
        next_player = (leg.ord % 2) + 1
        match.score_player1 = int(match.typus)
        match.score_player2 = int(match.typus)
    else:
        match_finished = False
        if player == match.player1:
            old_score = match.score_player1
            match.score_player1 -= throw_score
            next_player = 2
        elif player == match.player2:
            old_score = match.score_player2
            match.score_player2 -= throw_score
            next_player = 1
        else:
            return JsonResponse(

                {'success': False, 'reason': 'Player is not in match'},
                safe=False
            )
    match.score_player1 = max(match.score_player1, 0)
    match.score_player2 = max(match.score_player2, 0)
    match.save()
    return_data = {
        'success': True,
        'throw_score': throw_score,
        'old_score': old_score,
        'next_player': next_player,
        'match_finished': match_finished,
    }
    return JsonResponse(return_data, safe=False)


@login_required()
@require_http_methods(["GET"])
def get_checkout(request, remaining):
    checkout_url = getattr(settings, 'CHECKOUT_URL', None)
    if checkout_url is not None:
        resp = requests.get(
            f'{checkout_url}{remaining}'
        )
        if resp.status_code == 200:
            return JsonResponse(resp.json(), safe=False)
        return JsonResponse({'success': False, 'reason': resp.status_code})
    if 'test' in sys.argv:
        # Test, mock the service response
        return JsonResponse(
            {
                "darts": [
                    {"field": 19, "region": "Triple"},
                    {"field": 12, "region": "Triple"},
                    {"field": 13, "region": "Double"}
                ]
            },
            safe=False
        )
    return JsonResponse({'success': False, 'reason': 'CHECKOUT_URL not configured'})

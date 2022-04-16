import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
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
            Q(player1=self.request.user.player) | Q(player2=self.request.user.player),
            winner=None,
        )
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
            p1_turn = None
        try:
            p2_turn = leg.turns.filter(player=self.object.player2).latest('ord')
            ctx['p2_latest_score'] = p2_turn.throw1 + p2_turn.throw2 + p2_turn.throw3
            ctx['p2_old_score'] = self.object.score_player2 + ctx['p2_latest_score']
        except Turn.DoesNotExist:
            p2_turn = None
        if p1_turn and p2_turn:
            if p1_turn.ord < p2_turn.ord:
                ctx['active'] = 'player1'
            else:
                ctx['active'] = 'player2'
        else:
            ctx['active'] = 'player1'
        return ctx


def delete_match(request, match_id):
    Match.objects.get(pk=match_id).delete()
    return redirect(reverse('match:create'))


@require_http_methods(["POST"])
def save_turn(request, match_id):
    player_id = request.POST.get('player', None)
    if not player_id:
        return JsonResponse(json.dumps({'success': False, 'reason': 'No player provided'}))
    player = Player.objects.get(pk=player_id)
    throw1 = int(request.POST.get('throw1', 0))
    throw2 = int(request.POST.get('throw2', 0))
    throw3 = int(request.POST.get('throw3', 0))
    throw_score = throw1 + throw2 + throw3
    match = Match.objects.get(pk=match_id)
    leg = match.legs.last()
    ordinal = leg.turns.count() + 1
    Turn.objects.create(
        leg=leg,
        player=player,
        ord=ordinal,
        throw1=throw1,
        throw2=throw2,
        throw3=throw3,
    )
    if player == match.player1:
        old_score = match.score_player1
        match.score_player1 -= throw_score
    elif player == match.player2:
        old_score = match.score_player2
        match.score_player2 -= throw_score
    else:
        return JsonResponse(json.dumps({'success': False, 'reason': 'Player is not in match'}))
    match.save()
    return_data = {
        'success': True,
        'throw_score': throw_score,
        'old_score': old_score
    }
    return JsonResponse(json.dumps(return_data), safe=False)

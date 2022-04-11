from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
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
            Q(player1=self.request.user.player) | Q(player2=self.request.user.player)
        )
        return ctx


class MatchBoardView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'match/match_board.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['multipliers'] = [1, 2, 3]
        ctx['fields'] = range(1, 21)
        return ctx


def delete_match(request, match_id):
    Match.objects.get(pk=match_id).delete()
    return redirect(reverse('match:create'))


@require_http_methods(["POST"])
def save_turn(request, match_id):
    player_id = request.POST.get('player', None)
    throw1 = request.POST.get('throw1', 0)
    throw2 = request.POST.get('throw2', 0)
    throw3 = request.POST.get('throw3', 0)
    match = Match.objects.get(pk=match_id)
    leg = Leg.objects.create(match=match, ord=match.legs.count()+1)
    Turn.objects.create(
        leg=leg,
        player=Player.objects.get(pk=player_id),
        throw1=throw1,
        throw2=throw2,
        throw3=throw3,
    )
    return HttpResponse('success')

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from bootstrap_modal_forms.utils import is_ajax
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView, ListView, CreateView

from player.forms import PlayerForm, UserForm, LeagueForm, PlayerSelectForm
from player.models import Player, League


User = auth.get_user_model()


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('player:league-list')

    def form_valid(self, form):
        user = form.save(commit=True)
        player = Player.objects.create(
            user=user
        )
        if 'nickname' in form.changed_data:
            player.nickname = form.cleaned_data['nickname']
            player.save()
        league = League.objects.get(pk=self.kwargs['league_id'])
        league.players.add(player)
        return super().form_valid(form)


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerForm

    def get_object(self, queryset=None):
        # pylint: disable=unused-variable
        player, created = Player.objects.get_or_create(user=self.request.user)
        return player

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.object.user.email
        initial['first_name'] = self.object.user.first_name
        initial['last_name'] = self.object.user.last_name
        return initial

    def form_valid(self, form):
        player = form.save(commit=False)
        changed = False
        if 'username' in form.changed_data:
            player.user.username = form.cleaned_data['username']
            changed = True
        if 'email' in form.changed_data:
            player.user.email = form.cleaned_data['email']
            changed = True
        if 'first_name' in form.changed_data:
            player.user.first_name = form.cleaned_data['first_name']
            changed = True
        if 'last_name' in form.changed_data:
            player.user.last_name = form.cleaned_data['last_name']
            changed = True
        if changed:
            player.user.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')


class LeagueListView(LoginRequiredMixin, ListView):
    model = League

    def get_queryset(self):
        player = self.request.user.player
        return player.managed_leagues.all()


class LeagueCreateView(LoginRequiredMixin, BSModalCreateView):
    model = League
    form_class = LeagueForm

    def get_success_url(self):
        return reverse('player:league-list')

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            league = form.save(commit=False)
            league.save()
            league.managers.add(self.request.user.player)
        else:
            pass
        return redirect(self.get_success_url())


class LeagueUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = League
    form_class = LeagueForm

    def get_success_url(self):
        return reverse('player:league-list')


class PlayerAddToLeagueView(LoginRequiredMixin, BSModalUpdateView):
    model = League
    form_class = PlayerSelectForm
    template_name = 'player/league_add_player.html'

    def get_success_url(self):
        return reverse('player:league-list')


@require_http_methods(["GET"])
def get_players_for_league(request, league_id):
    players = League.objects.get(id=league_id).players.all()
    json_data = []
    for player in players:
        json_data.append({'value': player.id, 'text': str(player)})
    return JsonResponse(json_data, safe=False)

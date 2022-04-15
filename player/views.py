from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.urls import reverse
from django.views.generic import UpdateView, ListView, CreateView

from player.forms import PlayerForm, UserForm, LeagueForm, PlayerSelectForm
from player.models import Player, League


User = auth.get_user_model()


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('home')

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
        manager = self.request.user.player
        return manager.is_manager_for_league.all()


class LeagueCreateView(LoginRequiredMixin, CreateView):
    model = League
    form_class = LeagueForm

    def get_success_url(self):
        return reverse('player:league-list')

    def form_valid(self, form):
        league = form.save(commit=True)
        league.players.add(self.request.user.player)
        league.manager = self.request.user.player
        return super().form_valid(form)


class PlayerAddToLeagueView(LoginRequiredMixin, UpdateView):
    model = League
    form_class = PlayerSelectForm
    template_name = 'player/league_add_player.html'

    def get_success_url(self):
        return reverse('player:league-list')

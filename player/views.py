from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView, ListView

from player.forms import PlayerForm
from player.models import Player, League


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

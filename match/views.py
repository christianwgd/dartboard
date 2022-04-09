from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView

from match.forms import MatchForm
from match.models import Match


@login_required(login_url='/accounts/login/')
def board(request):
    fields = range(1, 21)
    return render(request, 'match/board.html', {
        "multipliers": [1, 2, 3],
        "fields": [fields[i:i + 4] for i in range(0, 20, 4)]
    })


class MatchCreateView(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchForm

    def get_success_url(self):
        return reverse('match:board')

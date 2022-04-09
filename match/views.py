from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/accounts/login/')
def board(request):
    fields = range(1, 21)
    return render(request, 'match/board.html', {
        "multipliers": [1, 2, 3],
        "fields": [fields[i:i + 4] for i in range(0, 20, 4)]
    })

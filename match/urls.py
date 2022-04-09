from django.urls import path

from match import views


app_name = 'match'

urlpatterns = [
    path('create/', views.MatchCreateView.as_view(), name='create'),
    path('board/', views.board, name='board'),
]

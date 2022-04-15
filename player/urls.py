from django.urls import path

from player import views


app_name = 'player'

urlpatterns = [
    path('create/<int:league_id>/', views.UserCreateView.as_view(), name='create'),
    path('update/', views.PlayerUpdateView.as_view(), name='update'),
    path('league-list/', views.LeagueListView.as_view(), name='league-list'),
    path('league-create/', views.LeagueCreateView.as_view(), name='league-create'),
    path('add_to_league/<int:pk>/', views.PlayerAddToLeagueView.as_view(), name='add-to-league'),

]

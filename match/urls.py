from django.urls import path

from match import views


app_name = 'match'

urlpatterns = [
    path('create/', views.MatchCreateView.as_view(), name='create'),
    path('board/<int:pk>/', views.MatchBoardView.as_view(), name='board'),
    path('delete/<int:match_id>/', views.delete_match, name='delete'),
]

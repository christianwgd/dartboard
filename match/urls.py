from django.urls import path

from match import views


app_name = 'match'

urlpatterns = [
    path('create/', views.MatchCreateView.as_view(), name='create'),
    path('board/<int:pk>/', views.MatchBoardView.as_view(), name='board'),
    path('summary/<int:pk>/', views.MatchSummaryView.as_view(), name='summary'),
    path('delete/<int:match_id>/', views.delete_match, name='delete'),
    path('save_turn/<int:match_id>/', views.save_turn, name='save_turn'),
    path('checkout/<int:remaining>/', views.get_checkout, name='checkout'),

    path('dart/<int:match_id>/<str:active>/<int:value>/', views.dart, name='dart'),
]

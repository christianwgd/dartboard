from django.urls import path

from match import views

app_name = "match"
urlpatterns = [
    path("board/", views.board, name="board"),
]


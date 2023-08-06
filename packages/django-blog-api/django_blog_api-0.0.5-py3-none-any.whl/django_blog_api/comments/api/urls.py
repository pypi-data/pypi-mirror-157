from django.urls import path

from .views import api_comments_lists

app_name = "posts"
urlpatterns = [
    path("comments/list", api_comments_lists, name='comments-list'),
]

from django.urls import path

from .views import api_comments_lists

app_name = "comments"
urlpatterns = [
    path("django-blog-api/comments/list", api_comments_lists, name='django-blog-api-comments-list'),
]

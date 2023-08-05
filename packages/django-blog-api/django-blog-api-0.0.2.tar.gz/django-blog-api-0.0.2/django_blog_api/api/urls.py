from django.urls import path, include

urlpatterns = [
    path("django-blog-api/", include("django_blog_api.posts.api.urls")),
]

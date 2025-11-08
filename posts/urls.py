from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="tweet_index"),
    path("create/", views.CreateTweet.as_view(), name="tweet_create"),
    path("<int:pk>/", views.DetailTweet.as_view(), name="tweet_detail"),
    path(
        "<int:pk>/comments/create/",
        views.CreateComment.as_view(),
        name="comment_create",
    ),
    path("<int:pk>/likes/", views.LikeTweet.as_view(), name="tweet_like"),
]

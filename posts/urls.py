from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("create/", views.CreateTweet.as_view(), name="create"),
    path("<int:pk>/", views.DetailTweet.as_view(), name="detail"),
]

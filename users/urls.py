from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "users"

urlpatterns = [
    path("", views.UserProfile.as_view(), name="profile"),
    path("edit/", views.UserProfileEdit.as_view(), name="profile_edit"),
    path("follows/", views.FollowUser.as_view(), name="user_follow"),
    path("bookmarks/", views.BookmarkIndex.as_view(), name="user_bookmark"),
    path("messages/", views.MessageIndex.as_view(), name="user_message"),
    path("messages/create", views.CreateMessage.as_view(), name="user_message_create"),
    path("notifies/", views.NotifyIndex.as_view(), name="user_notify"),
]

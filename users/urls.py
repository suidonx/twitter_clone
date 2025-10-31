from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "users"

urlpatterns = [
    path("", views.UserProfile.as_view(), name="profile"),
]

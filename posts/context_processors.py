from django.db import models

from accounts.models import CustomUser
from posts.models import Tweet
from users.models import Like


def sidebar(request):

    context = {}
    context["SIDEBAR"] = {}

    context["SIDEBAR"]["likest"] = Tweet.objects.annotate(
        cnt_like=models.Count("like")
    ).order_by("-cnt_like")[:3]
    context["SIDEBAR"]["follower"] = CustomUser.objects.annotate(
        cnt_follower=models.Count("followed")
    ).order_by("-cnt_follower")[:3]

    return context

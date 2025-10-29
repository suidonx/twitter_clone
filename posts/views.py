from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import ListView

from .models import Tweet
from users.models import Follow


# Create your views here.
class IndexView(ListView):
    model = Tweet
    template_name = "posts/top.html"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        parm = self.request.GET.get("tab", "recommend")

        if parm == "recommend":
            queryset = Tweet.objects.prefetch_related("user").order_by("-created_at")

        elif parm == "follow":
            if self.request.user.id is None:
                return queryset
            else:
                users = Follow.objects.filter(follower=self.request.user).values_list(
                    "followed"
                )

            queryset = (
                Tweet.objects.filter(user__in=users)
                .prefetch_related("user")
                .order_by("-created_at")
            )

        return queryset

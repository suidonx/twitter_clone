from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views.generic import DetailView

from posts.models import Tweet

CustomUser = get_user_model()


# Create your views here.
class UserProfile(DetailView):
    model = CustomUser
    slug_field = "account_id"
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        slug = self.kwargs["slug"]

        user = CustomUser.objects.filter(account_id=slug).first()
        tweets = (
            Tweet.objects.filter(user=user)
            .prefetch_related("user")
            .order_by("-created_at")
        )

        context["tweets"] = tweets

        return context

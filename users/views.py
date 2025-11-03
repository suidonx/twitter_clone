from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from .forms import ProfileEditForm
from .models import Like, Retweet, Comment
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

        # プロフィールページのユーザーを取得
        user = CustomUser.objects.filter(account_id=slug).first()

        param = self.request.GET.get("tab")

        # ユーザーがいいねしたツイート一覧を表示
        if param == "good":
            liked_tweet = Like.objects.filter(user=user).values_list(
                "tweet",
                flat=True,
            )
            tweets = (
                Tweet.objects.filter(id__in=liked_tweet)
                .prefetch_related("user", "tweetimage_set")
                .order_by("-created_at")
            )

        # ユーザーがリツイートしたツイート一覧を表示
        elif param == "retweet":
            retweeted_tweet = Retweet.objects.filter(user=user).values_list(
                "tweet",
                flat=True,
            )
            tweets = (
                Tweet.objects.filter(id__in=retweeted_tweet)
                .prefetch_related("user", "tweetimage_set")
                .order_by("-created_at")
            )
        # ユーザーがコメントしたツイート一覧を表示
        elif param == "comment":
            commented_tweet = Comment.objects.filter(user=user).values_list(
                "tweet",
                flat=True,
            )
            tweets = (
                Tweet.objects.filter(id__in=commented_tweet)
                .prefetch_related("user", "tweetimage_set")
                .order_by("-created_at")
            )

        # ユーザーのツイート一覧を表示
        else:
            tweets = (
                Tweet.objects.filter(user=user)
                .prefetch_related("user", "tweetimage_set")
                .order_by("-created_at")
            )

        # ページネーション
        paginator = Paginator(tweets, 5)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["tweets"] = page_obj.object_list

        return context


class UseProfileEdit(UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    slug_field = "account_id"
    template_name = "users/profile_edit.html"

    def get_success_url(self):
        return reverse("users:profile_edit", args=[self.object.account_id])

    def form_valid(self, form):
        messages.success(self.request, "ユーザープロフィールを更新しました")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.INFO,
            "ユーザープロフィールの更新に失敗しました",
            extra_tags="danger",
        )

        response = super().form_invalid(form)
        return response

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Prefetch
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

        # 場合分け用パラメーター
        param = self.request.GET.get("tab")

        # ユーザーがいいねしたツイート一覧を表示
        if param == "good":
            tweets = Tweet.objects.filter(like__user=user).order_by("-like__created_at")

        # ユーザーがリツイートしたツイート一覧を表示
        elif param == "retweet":
            tweets = Tweet.objects.filter(retweet__user=user).order_by(
                "-retweet__created_at"
            )

        # ユーザーがコメントしたツイート一覧を表示
        elif param == "comment":
            tweets = Tweet.objects.filter(comment__user=user).order_by(
                "-comment__created_at"
            )

        # ユーザーのツイート一覧を表示
        else:
            tweets = Tweet.objects.filter(user=user).order_by("-created_at")

        # コンテキストに渡すツイート一覧を取得
        tweets = (
            tweets.select_related("user")
            .prefetch_related("tweetimage_set", "like_set", "retweet_set")
            .prefetch_related(
                Prefetch(
                    "like_set",
                    queryset=Like.objects.filter(user=self.request.user),
                    to_attr="user_liked_tweet",
                )
            )
            .prefetch_related(
                Prefetch(
                    "retweet_set",
                    queryset=Retweet.objects.filter(user=self.request.user),
                    to_attr="user_retweeted_tweet",
                )
            )
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

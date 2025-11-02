from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import DetailView

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

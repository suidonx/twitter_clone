from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, UpdateView, View, ListView

from .forms import ProfileEditForm, MessageForm
from .models import Like, Retweet, Comment, Follow, Bookmark, Message
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
            .prefetch_related(
                Prefetch(
                    "bookmark_set",
                    queryset=Bookmark.objects.filter(
                        user=self.request.user,
                    ),
                    to_attr="user_bookmarkd_tweet",
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


class UserProfileEdit(UpdateView):
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


class FollowUser(View):
    def get(self, request, slug):
        return redirect(reverse("posts:tweet_index"))

    def post(self, request, slug):
        follower = self.request.user
        followed = get_object_or_404(CustomUser, account_id=slug)

        follow, is_created = Follow.objects.get_or_create(
            follower=follower,
            followed=followed,
        )

        if is_created:
            messages.success(self.request, "フォローに成功しました")

        else:
            follow.delete()
            messages.warning(self.request, "フォローを解除しました")

        return redirect(self.request.META.get("HTTP_REFERER", "/"))


class BookmarkIndex(ListView):
    model = Tweet
    template_name = "users/bookmark.html"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.id is None:
            return queryset

        # ユーザーがブックマークしたツイート一覧を表示
        else:
            queryset = (
                Tweet.objects.filter(bookmark__user=self.request.user)
                .select_related("user")
                .prefetch_related(
                    "tweetimage_set",
                    "like_set",
                    "retweet_set",
                )
                .prefetch_related(
                    Prefetch(
                        "like_set",
                        queryset=Like.objects.filter(
                            user=self.request.user,
                        ),
                        to_attr="user_liked_tweet",
                    )
                )
                .prefetch_related(
                    Prefetch(
                        "retweet_set",
                        queryset=Retweet.objects.filter(
                            user=self.request.user,
                        ),
                        to_attr="user_retweeted_tweet",
                    )
                )
                .prefetch_related(
                    Prefetch(
                        "bookmark_set",
                        queryset=Bookmark.objects.filter(
                            user=self.request.user,
                        ),
                        to_attr="user_bookmarkd_tweet",
                    )
                )
                .order_by("-bookmark__created_at")
            )

        return queryset


class MessageIndex(ListView):
    model = Message
    template_name = "users/message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        followers = Follow.objects.filter(followed=user).select_related(
            "follower",
        )

        # userパラメーターの取得
        opponent = self.request.GET.get("user")

        if opponent:
            opponent = get_object_or_404(
                CustomUser, account_id=self.request.GET.get("user")
            )

            # ユーザーと相手のメッセージのやり取りを取得
            messages = Message.objects.filter(sender__in=[user, opponent]).filter(
                recipient__in=[user, opponent]
            )

            context["user_messages"] = messages

        context["followers"] = followers
        return context


class CreateMessage(View):
    def get(self, request, slug):
        return redirect(reverse("posts:index"))

    def post(self, request, slug):
        sender = self.request.user
        account_id = self.request.GET.get("user")
        recipient = CustomUser.objects.get(account_id=account_id)
        content = self.request.POST.get("content")

        form = MessageForm(
            {
                "sender": sender,
                "recipient": recipient,
                "content": content,
            }
        )

        if form.is_valid():
            form.save()
            messages.success(self.request, "メッセージを投稿しました")

        else:
            messages.add_message(
                self.request,
                messages.INFO,
                "メッセージの投稿に失敗しました",
                extra_tags="danger",
            )

        return redirect(self.request.META.get("HTTP_REFERER", "/"))

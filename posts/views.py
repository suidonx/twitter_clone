from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView, View, DetailView

from .forms import (
    CreateTweetForm,
    CreateTweetImageForm,
    CreateCommentForm,
)
from .models import Tweet
from users.models import (
    Follow,
    Comment,
    Like,
    Retweet,
    Bookmark,
    LikeNotify,
    RetweetNotify,
    CommentNotify,
)


# Create your views here.
class IndexView(ListView):
    model = Tweet
    template_name = "posts/top.html"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        parm = self.request.GET.get("tab", "recommend")

        if parm == "recommend":
            if self.request.user.id is None:
                return queryset
            else:
                queryset = (
                    Tweet.objects.select_related("user")
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
                    .order_by("-created_at")
                )

        elif parm == "follow":
            if self.request.user.id is None:
                return queryset
            else:
                users = Follow.objects.filter(follower=self.request.user).values_list(
                    "followed",
                    flat=True,
                )

            queryset = (
                Tweet.objects.filter(user__in=users)
                .select_related("user")
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
                .order_by("-created_at")
            )

        return queryset


class CreateTweet(View):
    def get(self, request):
        return redirect(reverse("posts:tweet_index"))

    def post(self, request):

        def _post_success():
            messages.success(self.request, "ポストに成功しました")

        def _post_error():
            messages.add_message(
                self.request,
                messages.INFO,
                "ポストに失敗しました",
                extra_tags="danger",
            )

        def _image_error():
            messages.add_message(
                self.request,
                messages.INFO,
                "画像の投稿に失敗しました",
                extra_tags="danger",
            )

        def _not_found_post():
            messages.warning(self.request, "ポスト内容がありません")

        # POST通信で受け取った値を格納
        content = self.request.POST.get("content")
        image = self.request.FILES.get("image")

        # モデルフォームインスタンスを生成
        content_form = CreateTweetForm(self.request.POST)
        image_form = CreateTweetImageForm(None, self.request.FILES)

        # ツイートと画像が投稿されたとき
        if content and image:

            # ツイートと画像のバリデーションが成功したとき
            if content_form.is_valid() and image_form.is_valid():

                # ツイートを保存
                tweet = content_form.save(commit=False)
                tweet.user = self.request.user
                tweet.save()

                # ツイートと画像インスタンスを紐づけて画像を保存
                image_form.instance.tweet = tweet
                image_form.save()

                _post_success()

            # 画像のバリデーションだけ成功
            elif image_form.is_valid():
                _post_error()

            # ツイートのバリデーションだけ成功
            elif content_form.is_valid():
                _image_error()

            # どちらのバリデーションも失敗
            else:
                _post_error()
                _image_error()

        # ツイートのみ投稿
        elif content:
            if content_form.is_valid():
                tweet = content_form.save(commit=False)
                tweet.user = self.request.user
                tweet.save()

                _post_success()

            else:
                _post_error()

        # ツイートなし、添付ファイルのみ投稿
        else:
            _not_found_post()

        return redirect(reverse("posts:tweet_index"))


class DetailTweet(DetailView):
    model = Tweet
    template_name = "posts/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get("pk")
        tweet = get_object_or_404(Tweet, id=pk)

        # コメントの取得
        comments = Comment.objects.filter(tweet=tweet).select_related("user")
        context["comments"] = comments

        return context

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()

        queryset = queryset.select_related("user")
        return queryset


class CreateComment(View):
    def get(self, request, pk):
        return redirect(reverse("posts:tweet_detail", args=[pk]))

    def post(self, request, pk):
        form_data = {
            "user": self.request.user.id,
            "tweet": Tweet.objects.get(id=pk),
            "content": self.request.POST.get("content"),
        }
        form = CreateCommentForm(form_data)

        if form.is_valid():
            comment = form.save()
            messages.success(self.request, "コメントに成功しました")

            # コメントをした場合、通知用のレコードを作成
            user = self.request.user
            tweet = Tweet.objects.get(id=pk)

            # 自分以外が自分のツイートにアクションを起こした場合、通知処理をする。
            if not user == tweet.user:
                CommentNotify.objects.create(user=tweet.user, comment=comment)

                # 相手に通知メールを送る
                send_mail(
                    subject="ツイートへの新着コメント",
                    message=render_to_string(
                        "users/notification_mail.txt",
                        {
                            "username": user.username,
                            "task": "コメント",
                            "comment": comment.content,
                        },
                    ),
                    from_email=None,
                    recipient_list=[tweet.user.email],
                )

        else:
            messages.add_message(
                self.request,
                messages.INFO,
                "コメントに失敗しました",
                extra_tags="danger",
            )

        return redirect(reverse("posts:tweet_detail", args=[pk]))


class LikeTweet(View):
    def get(self, request, pk):
        return redirect(reverse("posts:tweet_index"))

    def post(self, request, pk):

        user = self.request.user
        tweet = Tweet.objects.get(id=pk)

        # 未登録ならいいねを登録
        # すでに登録済みならそのオブジェクトを返して削除処理
        like, is_created = Like.objects.get_or_create(
            user=user,
            tweet=tweet,
        )

        if is_created:
            messages.success(self.request, "いいねに成功しました")

            # いいねがあった場合、通知用のレコードを作成
            # 自分以外が自分のツイートにアクションを起こした場合、通知処理をする。
            if not user == tweet.user:
                LikeNotify.objects.create(user=tweet.user, like=like)

                # 相手に通知メールを送る
                send_mail(
                    subject="ツイートへの新着いいね",
                    message=render_to_string(
                        "users/notification_mail.txt",
                        {
                            "username": user.username,
                            "task": "いいね",
                        },
                    ),
                    from_email=None,
                    recipient_list=[tweet.user.email],
                )

        else:
            like.delete()
            messages.success(self.request, "いいね解除しました")

        return redirect(self.request.META.get("HTTP_REFERER", "/"))


class RetweetTweet(View):
    def get(self, request, pk):
        return redirect(reverse("posts:tweet_index"))

    def post(self, request, pk):

        user = self.request.user
        tweet = Tweet.objects.get(id=pk)

        # 未登録ならリツイート
        # すでに登録済みならそのオブジェクトを返して削除処理
        retweet, is_created = Retweet.objects.get_or_create(
            user=user,
            tweet=tweet,
        )

        if is_created:
            messages.success(self.request, "リツイートに成功しました")

            # リツイートがあった場合、通知用のレコードを作成
            # 自分以外が自分のツイートにアクションを起こした場合、通知処理をする。
            if not user == tweet.user:
                RetweetNotify.objects.create(user=tweet.user, retweet=retweet)

                # 相手に通知メールを送る
                send_mail(
                    subject="ツイートへの新着リツイート",
                    message=render_to_string(
                        "users/notification_mail.txt",
                        {
                            "username": user.username,
                            "task": "リツイート",
                        },
                    ),
                    from_email=None,
                    recipient_list=[tweet.user.email],
                )

        else:
            retweet.delete()
            messages.success(self.request, "リツイートを解除しました")

        return redirect(self.request.META.get("HTTP_REFERER", "/"))


class BookmarkTweet(View):
    def get(self, request, pk):
        return redirect(reverse("posts:tweet_index"))

    def post(self, request, pk):

        user = self.request.user
        tweet = Tweet.objects.get(id=pk)

        # 未登録ならブックマーク
        # すでに登録済みならそのオブジェクトを返して削除処理
        bookmark, is_created = Bookmark.objects.get_or_create(
            user=user,
            tweet=tweet,
        )

        if is_created:
            messages.success(self.request, "ブックマークに成功しました")

        else:
            bookmark.delete()
            messages.success(self.request, "ブックマークを解除しました")

        return redirect(self.request.META.get("HTTP_REFERER", "/"))

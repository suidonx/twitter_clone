from django.db import models

from accounts.models import CustomUser
from posts.models import Tweet


# Create your models here.
class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    followed = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="followed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"],
                name="follows_unique",
            )
        ]


class Like(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="like_unique",
            )
        ]


class Retweet(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="retweet_unique",
            )
        ]


class Comment(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
    )
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Bookmark(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tweet"],
                name="bookmark_unique",
            )
        ]


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sender",
    )
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipient",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LikeNotify(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    like = models.ForeignKey(
        Like,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "like"],
                name="like_notify_unique",
            )
        ]


class RetweetNotify(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    retweet = models.ForeignKey(
        Retweet,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "retweet"],
                name="retweet_notify_unique",
            )
        ]


class CommentNotify(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="comment_notify_unique",
            )
        ]

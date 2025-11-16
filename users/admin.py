from django.contrib import admin

from .models import (
    Follow,
    Like,
    Retweet,
    Comment,
    Message,
    LikeNotify,
    RetweetNotify,
    CommentNotify,
)

# Register your models here.
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Retweet)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(LikeNotify)
admin.site.register(RetweetNotify)
admin.site.register(CommentNotify)

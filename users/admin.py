from django.contrib import admin

from .models import Follow, Like, Retweet, Comment, Message

# Register your models here.
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Retweet)
admin.site.register(Comment)
admin.site.register(Message)

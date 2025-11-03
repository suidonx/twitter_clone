from django.contrib import admin

from .models import Follow, Like, Retweet, Comment

# Register your models here.
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Retweet)
admin.site.register(Comment)

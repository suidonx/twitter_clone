from django.contrib import admin

from .models import Tweet, TweetImage

# Register your models here.
admin.site.register(Tweet)
admin.site.register(TweetImage)

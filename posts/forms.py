from django import forms

from .models import Tweet, TweetImage
from users.models import Comment


class CreateTweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ["user", "content"]


class CreateTweetImageForm(forms.ModelForm):
    class Meta:
        model = TweetImage
        fields = ["image"]


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["user", "tweet", "content"]

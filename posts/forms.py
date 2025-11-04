from django import forms

from .models import Tweet, TweetImage


class CreateTweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ["user", "content"]


class CreateTweetImageForm(forms.ModelForm):
    class Meta:
        model = TweetImage
        fields = ["image"]

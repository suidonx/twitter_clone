from django.shortcuts import render
from django.views.generic import ListView

from .models import Tweet


# Create your views here.
class IndexView(ListView):
    model = Tweet
    template_name = "posts/top.html"

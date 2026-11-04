from django.shortcuts import render
from django.contrib import UserCreation


def landing_page(request):
    return render(request, "index.html")


def register(request):
    form = UserCreation
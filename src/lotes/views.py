from django.shortcuts import render
from django.db import connections


def index(request):
    context = {
    }
    return render(request, 'lotes/index.html', context)

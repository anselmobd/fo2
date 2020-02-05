from django.views import View
from django.shortcuts import render


def index(request):
    return render(request, 'email_signature/index.html')


def show_template(request):
    return render(request, 'email_signature/assin-abvtex.html')

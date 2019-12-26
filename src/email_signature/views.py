from django.views import View
from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'email_signature/index.html', context)


class Accounts(View):
    pass

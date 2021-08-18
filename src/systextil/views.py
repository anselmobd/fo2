from pprint import pprint, pformat

from django.shortcuts import render


def index(request):
    return render(request, 'systextil/index.html')


def sessions(request):
    json = {'teste': "Teste!"}
    context = {
        "titulo": "Sessions",
        "json": pformat(json),
    }
    return render(request, 'systextil/sessions.html', context)

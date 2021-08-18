import requests
from pprint import pprint, pformat

from django.shortcuts import render


def index(request):
    return render(request, 'systextil/index.html')


def sessions(request):
    req = requests.get('http://oc.tussor.com.br/systextil/sessions')
    json = req.json()
    context = {
        "titulo": "Sessions",
        "json": pformat(json),
    }
    return render(request, 'systextil/sessions.html', context)

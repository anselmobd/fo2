import requests
from pprint import pprint, pformat

from django.shortcuts import render


def index(request):
    return render(request, 'systextil/index.html')


def get_sessions():
    urls = [
        "http://oc.tussor.com.br/systextil/sessions",
        "http://tussor.systextil.com.br/systextil/sessions",
    ]
    for u in urls:
        try:
            req = requests.get(u, timeout=10)
        except requests.exceptions.ConnectTimeout:
            continue
        if req.status_code == 200:
            return pformat(req.json())
    return ""


def sessions(request):
    context = {
        "titulo": "Sessions",
        "json": get_sessions()
    }
    return render(request, 'systextil/sessions.html', context)

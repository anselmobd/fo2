import datetime
import requests
from pprint import pprint

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
            return req.json()
    return {}


def sessions(request):
    context = {"titulo": "Sessions"}
    json = get_sessions()

    dados = []
    if "sessions" in json:
        for session in json["sessions"]:
            row = {
                "ip": session["clientId"],
                "timestamp": session["startTimestamp"],
            }
            dados.append(row)

    for row in dados:
        row['desde'] = datetime.datetime.fromtimestamp(row['timestamp']/1000.0)

    dados = sorted(dados, key=lambda k: k['desde']) 

    context.update({
        "headers": ["IP", "Desde"],
        "fields": ["ip", "desde"],
        "dados": dados,
    })
    return render(request, 'systextil/sessions.html', context)

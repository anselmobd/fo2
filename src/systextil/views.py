import datetime
from pprint import pprint

from django.shortcuts import render

from systextil.functions import get_sessions


def index(request):
    return render(request, 'systextil/index.html')


def sessions(request):
    context = {"titulo": "Seções"}
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

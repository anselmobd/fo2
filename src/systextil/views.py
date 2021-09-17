import datetime
from pprint import pprint

from django.shortcuts import render

from systextil.functions import get_sessions


def index(request):
    return render(request, 'systextil/index.html')


def sessions(request):
    context = {"titulo": "Seções"}
    json = get_sessions()

    ips = {}
    if "sessions" in json:
        for session in json["sessions"]:
            ip = session["clientId"]
            desde = datetime.datetime.fromtimestamp(session["startTimestamp"]/1000.0)
            desde_str = desde.strftime('%d/%m/%Y %H:%M:%S')
            if ip in ips:
                row = ips[ip]
                if desde < row["desde"]:
                    row["desde"] = desde
                    row["desde_str"] = ", ".join([desde_str, row["desde_str"]])
                else:
                    row["desde_str"] = ", ".join([row["desde_str"], desde_str])
            else:
                ips[ip] = {
                    "ip": ip,
                    "desde": desde,
                    "desde_str": desde_str,
                }

    dados = sorted(ips.values(), key=lambda k: k['desde']) 

    context.update({
        "headers": ["IP", "Desde"],
        "fields": ["ip", "desde_str"],
        "dados": dados,
    })
    return render(request, 'systextil/sessions.html', context)

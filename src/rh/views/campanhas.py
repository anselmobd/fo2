from pprint import pprint

from django.shortcuts import render


def campanhas(request, id):
    if id is None:
        context = {'titulo': 'Campanhas'}
        return render(request, 'rh/campanhas.html', context)
    elif id == '2020-01-22':
        return render(request, 'rh/campanhas/2020-01-22-RS-IT.html')
    elif id == '2020-02-11':
        return render(request, 'rh/campanhas/2020-02-11-premiacao.html')
    elif id == '2020-03-12':
        return render(
            request, 'rh/campanhas/2020-03-12-reunioes-produtivas.html')
    elif id == '2020-09-01':
        return render(
            request, 'rh/campanhas/2020-09-01-setembro-amarelo.html')
    elif id == '2020-10-14':
        return render(
            request, 'rh/campanhas/2020-10-14-outubro-rosa.html')
    elif id == '2020-11-27':
        return render(
            request, 'rh/campanhas/2020-11-27-agentes.html')

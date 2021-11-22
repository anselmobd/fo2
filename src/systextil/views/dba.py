from pprint import pprint

from django.shortcuts import render


def demorada(request):
    return render(request, 'systextil/dba/demorada.html')

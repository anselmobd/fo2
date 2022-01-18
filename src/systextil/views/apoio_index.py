from pprint import pprint

from django.shortcuts import render


def view(request):
    return render(request, 'systextil/apoio_index.html')

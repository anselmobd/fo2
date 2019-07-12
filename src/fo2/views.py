import logging

from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.http import HttpResponse

from utils.functions import get_client_ip


fo2logger = logging.getLogger('fo2')


def index_view(request):
    fo2logger.info('index')
    return redirect('apoio_ao_erp')


def test_view(request):
    context = {}
    return render(request, 'test.html', context)


class ApoioAoErpView(TemplateView):
    template_name = "index.html"


class IntranetView(TemplateView):
    template_name = "intranet.html"


def myip_view(request):
    return HttpResponse("Your IP is : {}".format(get_client_ip(request)))


def ack_view(request):
    return HttpResponse("Ack")


class SystextilView(TemplateView):
    template_name = "oficial_systextil.html"

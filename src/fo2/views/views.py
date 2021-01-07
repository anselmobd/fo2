from pprint import pprint

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import TemplateView, View

from base.models import Colaborador

from utils.classes import AcessoInterno
from utils.functions import get_client_ip, fo2logger
from utils.functions.ssh import router_add_ip_apoio_auth


def index_tussor_view(request):
    fo2logger.info('index')
    return redirect('apoio_ao_erp')


def index_agator_view(request):
    fo2logger.info('index')
    return HttpResponse("Agator")


def test_view(request):
    context = {}
    return render(request, 'test.html', context)


class ApoioAoErpView(TemplateView):
    template_name = "index.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = super(ApoioAoErpView, self).get_context_data(
    #         *args, **kwargs)
    #     context['logged_count'] = Colaborador.objects.filter(
    #         logged=True).count()
    #     return context


class IntranetView(TemplateView):
    template_name = "intranet.html"


def myip_view(request):
    return HttpResponse("Your IP is : {}".format(get_client_ip(request)))


def meuip_view(request):
    return HttpResponse("Seu IP é : {}".format(get_client_ip(request)))


def ack_view(request):
    return HttpResponse("Ack")


class SystextilView(View):
    def get(self, request, *args, **kwargs):
        acesso_interno = AcessoInterno()
        try:
            acesso_externo = not acesso_interno.current_interno
        except Exception:
            acesso_externo = False
        context = {
            'externo': acesso_externo,
        }
        return render(request, "oficial_systextil.html", context)


def router_ip_to_apoio_auth(request):
    result = router_add_ip_apoio_auth(get_client_ip(request))
    return JsonResponse(result, safe=False)

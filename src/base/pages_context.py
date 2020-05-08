from pprint import pprint

from utils.classes import AcessoInterno

from base.models import Colaborador


def get_origem_do_ip(request):
    acesso_interno = AcessoInterno()
    try:
        ip_interno = acesso_interno.current_interno
        ip_externo = not ip_interno
        ip_de_acesso = True
    except Exception:
        ip_interno = False
        ip_externo = False
        ip_de_acesso = False
    context = {
        'base_ip_interno': ip_interno,
        'base_ip_externo': ip_externo,
        'base_ip_de_acesso': ip_de_acesso,
    }
    return context


def get_logged_n(request):
    context = {
        'logged_n': Colaborador.objects.filter(logged=True).count(),
    }
    return context

from pprint import pprint

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone

from utils.classes import AcessoInterno

from base.models import Colaborador


def get_current_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    return User.objects.filter(id__in=user_id_list)


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


def get_logged_count(request):
    queryset = get_current_users()
    context = {
        'logged_count': queryset.count(),
    }
    return context


def main(request):
    context = {}
    context.update(get_origem_do_ip(request))
    context.update(get_logged_count(request))
    return context

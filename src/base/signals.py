from http.cookies import SimpleCookie
from pprint import pprint

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.core.signals import request_started
from django.dispatch import receiver
from django.utils import timezone

from utils.classes import AcessoInterno

from .models import Colaborador, Requisicao
from .queries.models import get_create_colaborador_by_user


@receiver(request_started)
def request_start(sender, environ, **kwargs):
    passo = 1
    if 'HTTP_COOKIE' in environ:
        cookies = SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        passo += 1

    if passo == 2:
        try:
            sessionid = cookies['sessionid'].value
            passo += 1
        except Exception:
            pass

    if passo == 3:
        try:
            session = Session.objects.get(session_key=sessionid)
            passo += 1
        except Session.DoesNotExist:
            pass

    if passo == 4:
        try:
            data = session.get_decoded()
            passo += 1
        except AttributeError:
            pass

    if passo == 5:
        try:
            user_id = data.get('_auth_user_id', None)
            passo += 1
        except AttributeError:
            pass

    if passo == 6:
        try:
            colab = Colaborador.objects.get(user__id=user_id)
        except Colaborador.DoesNotExist:
            colab = None
    else:
        colab = None

    req = Requisicao(
        colaborador=colab,
        request_method=environ['REQUEST_METHOD'],
        path_info=environ['PATH_INFO'],
        http_accept=environ['HTTP_ACCEPT'],
        quando=timezone.now(),
        ip=environ['REMOTE_ADDR'],
    )
    req.save()


@receiver(user_logged_in)
def login_user(sender, user, request, **kwargs):
    colab = get_create_colaborador_by_user(user)

    try:
        colab.logged = True
        colab.quando = timezone.now()

        acesso_interno = AcessoInterno()
        try:
            colab.ip_interno = acesso_interno.current_interno
        except Exception:
            pass

        colab.save()
    except Exception:
        pass


@receiver(user_logged_out)
def logout_user(sender, user, request, **kwargs):
    try:
        colab = Colaborador.objects.get(user__username=user.username)
        colab.logged = False
        colab.quando = timezone.now()
        colab.save()
    except Colaborador.DoesNotExist:
        pass

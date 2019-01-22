from django.urls import reverse

from .models import Painel, PainelModulo, PopAssunto


# http://kkabardi.me/post/dynamic-menu-navigation-django/
def get_list_geral_paineis(context):
    paineis = None
    modulos = None
    popAssuntos = None
    if context.environ['PATH_INFO'] in [
            reverse('apoio_ao_erp'),
            reverse('geral:index')]:
        paineis = Painel.objects.all()
        modulos = PainelModulo.objects.all().order_by('nome')
        popAssuntos = PopAssunto.objects.all().order_by('nome')
    return {'list_geral_paineis': paineis,
            'list_geral_modulos': modulos,
            'list_geral_pop_assuntos': popAssuntos,
            }


def request_user(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    return user


def has_permission(request, permission):
    can = False
    user = request_user(request)
    if user:
        can = user.has_perm(permission)
    return can

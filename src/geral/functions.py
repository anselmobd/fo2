from pprint import pprint

from django.urls import reverse
from django.template.defaulttags import register
from django.db.models import Min

from .models import Painel, PainelModulo, PopAssunto
import geral.models as models


# http://kkabardi.me/post/dynamic-menu-navigation-django/
def get_list_geral_paineis(context):
    paineis = None
    modulos = None
    popAssuntos = None
    if context.environ['PATH_INFO'] in [
            reverse('apoio_ao_erp'),
            reverse('geral:index')]:
        paineis = Painel.objects.filter(habilitado=True)
        modulos = PainelModulo.objects.filter(habilitado=True).order_by('nome')
        popAssuntos = PopAssunto.objects.all().order_by('nome')
    return {'list_geral_paineis': paineis,
            'list_geral_modulos': modulos,
            'list_geral_pop_assuntos': popAssuntos,
            }


@register.filter
def list_geral(data):
    if data == 'pop_assuntos_grupos':
        return PopAssunto.objects.exclude(grupo_slug='').values(
            'grupo').annotate(Min('grupo_slug')).order_by('grupo')
    return ''


@register.filter
def list_geral_filtro(data, filtro):
    if data == 'pop_assuntos':
        filtro_list = filtro.split('==')
        filtro_dict = {filtro_list[0]: filtro_list[1]}
        return PopAssunto.objects.filter(**filtro_dict).order_by('nome')
    return ''


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


def coalesce(value, default=None):
    if value is None:
        return default
    else:
        return value


def config_get_typed_value(config):
    type = config.parametro.tipo.codigo
    if type == 'SN':
        return config.valor
    if type == 'I':
        try:
            return int(config.valor)
        except Exception:
            pass
    return None


def config_get_value(param_codigo, usuario=None, default=None):
    try:
        param = models.Parametro.objects.get(codigo=param_codigo)
    except models.Parametro.DoesNotExist:
        return default

    result = default
    try:
        config = models.Config.objects.get(parametro=param, usuario=None)
        result = config_get_typed_value(config)
    except models.Config.DoesNotExist:
        pass

    if usuario is None:
        return coalesce(result, default)

    if usuario.is_authenticated:
        try:
            config = models.Config.objects.get(
                parametro=param, usuario=usuario)
            result = config_get_typed_value(config)
        except models.Config.DoesNotExist:
            pass

    return coalesce(result, default)


def config_set_value(param_codigo, value, usuario=None):
    try:
        param = models.Parametro.objects.get(codigo=param_codigo)
    except models.Parametro.DoesNotExist:
        return False

    try:
        config = models.Config.objects.get(parametro=param, usuario=usuario)
        if config.valor != value:
            config.valor = value
            config.save()
    except Exception as e:
        return False

    return True

import datetime
import re
import yaml
from pprint import pprint
from pytz import utc

from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaulttags import register
from django.db.models import Min

import utils.functions.strings

from lotes.classes import YamlUser

import geral.models as models
import geral.queries
from .models import Painel, PainelModulo, PopAssunto


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

    config = None
    try:
        config = models.Config.objects.get(parametro=param, usuario=usuario)
    except models.Config.DoesNotExist as e:
        pass

    if config is None:
        try:
            config = models.Config.objects.get(parametro=param, usuario=None)
        except models.Config.DoesNotExist as e:
            pass

    if config is None:
        return False
    else:
        if config.valor != value:
            config.valor = value
            config.save()

    return True


def depositos_choices(
        cod_todos=None, descr_todos=None, cod_only=None,
        only=None, less=None, rest=None):
    CHOICES = []

    todos = []
    if cod_todos is not None:
        if descr_todos is None and only is not None:
            todos = [
                {'COD': cod_todos,
                 'DESCR': f"TODOS ({', '.join(map(str, only))})",
                 }]
        else:
            todos = [
                {'COD': cod_todos,
                 'DESCR': descr_todos,
                 }]

    grupo = []
    if cod_only is not None and only is not None:
        descr = utils.functions.strings.join((', ', ' e '), map(str, only))
        descr = f'({descr})'
        grupo = [
            {'COD': cod_only,
             'DESCR': descr,
             }]

    depositos_only = []
    if only is not None:
        depositos_only = geral.queries.deposito(only=only)

    if rest is not None:
        if rest:
            less = only

    depositos_less = []
    if less is not None:
        depositos_less = geral.queries.deposito(less=less)

    for deposito in (todos + grupo + depositos_only + depositos_less):
        if deposito['COD'] in (cod_todos, cod_only):
            descr = deposito['DESCR']
        else:
            descr = f"{deposito['COD']} - {deposito['DESCR']}"
            if deposito['COD'] <= 2:
                continue
        CHOICES.append((
            deposito['COD'],
            descr
        ))

    return CHOICES


def rec_trac_log_to_dict(log, log_version=1):
    if log_version == 1:
        log = log.replace("<UTC>", "utc")
        log = re.sub(
            r'^(.*)<DstTzInfo \'America/Sao_Paulo\' -03-1 day, '
            r'21:00:00 STD>(.*)$',
            r'\1utc\2', log)
        log = re.sub(
            r'^(.*)<SimpleLazyObject: <User: ([^\s]*)>>(.*)$',
            r'\1"\2"\3', log)
        log = re.sub(
            r'^(.*)<User: ([^\s]*)>(.*)$',
            r'\1"\2"\3', log)
        dic = eval(log)
    elif log_version == 2:
        dic = yaml.load(log)
        for key in dic:
            if isinstance(dic[key], YamlUser):
                dic[key] = dic[key].object_instance
    return dic


def log_version_by_table(table):
    table_dict = {
        'Lote': 2,
        'SolicitaLote': 2,
    }
    return table_dict[table]


def dict_to_rec_trac_log(dic, log_version=1):
    if log_version == 1:
        return dic
    elif log_version == 2:
        for key in dic:
            if isinstance(dic[key], User):
                dic[key] = YamlUser(dic[key])
        return yaml.dump(dic)

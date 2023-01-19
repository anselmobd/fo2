import base64
import re
from pprint import pprint

from django.template.defaulttags import register

import base.models

from utils.classes import GitVersion


@register.simple_tag
def git_ver():
    '''
    Retrieve and return the latest git commit hash ID and date
    Use in template:  {% git_ver %}
    '''
    git_version = GitVersion()
    return git_version.version


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def list_append(list1, value):
    if list1:
        if not isinstance(list1, list):
            list1 = [list1]
    else:
        list1 = []
    if value:
        list1.append(value)
    return list1


@register.filter
def if_text_sufix(text, sufix):
    return f"{text}{sufix}" if text else ''


@register.filter
def if_text_prefix(text, prefix):
    return f"{prefix}{text}" if text else ''


@register.filter
def gets_without(gets, var):
    list_gets = gets.split("&")
    clean_gets = [
        get
        for get in list_gets
        if not get.startswith(f"{var}=")
    ]
    return "&".join(clean_gets)


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


@register.filter
def zfill(s, len):
    s = str(s)
    return s.zfill(len)


@register.filter
def num_zfill(s, len):
    s = str(s)
    if s.isdigit():
        return s.zfill(len)
    else:
        return s


@register.filter
def transp_decimals(text):
    separa_zeros = re.compile("^(.*\,[^0]*)(0*)$")
    reg = separa_zeros.search(text)
    if reg:
        zeros = reg.group(2)
        if zeros:
            inicio = reg.group(1)
            if inicio[-1] == ',':
                inicio = inicio[:-1]
                zeros = ','+zeros
            return ''.join([
                inicio,
                '<span style="opacity: 0.7; position: static; z-index: -1;">',
                zeros,
                '</span>'])
    return text


@register.filter
def word_slice(text, slice):

    def adjust_cut(text, valor, limit=1):
        val = valor
        while val > 1 and text[val-1] != ' ':
            val -= 1
        if val <= limit:
            val = valor
        while val < len(text) and text[val] == ' ':
            val += 1
        return val

    if text == '':
        return text

    slices = slice.split(':')
    inicio = int(slices[0]) if slices[0] != '' else 0
    if inicio > len(text):
        return ''
    inicio = adjust_cut(text,  inicio)

    fim = int(slices[1]) if slices[1] != '' else len(text)
    if fim < inicio or fim < 0:
        return ''
    if fim < len(text):
        fim = adjust_cut(text,  fim)

    return text[inicio:fim]


@register.filter
def subtract(value, arg):
    return value - arg


def image_to_data_url(filename):
    ext = filename.split('.')[-1]
    prefix = f'data:image/{ext};base64,'
    with open(filename, 'rb') as f:
        img = f.read()
    return prefix + base64.b64encode(img).decode('utf-8')


@register.simple_tag
def data_url_image(tipo, imagem):
    try:
        imagem = base.models.Imagem.objects.get(
            grupo_arquivo__slug=tipo,
            slug=imagem,
        )
        return image_to_data_url(imagem.imagem.path)
    except base.models.Imagem.DoesNotExist:
        return ''

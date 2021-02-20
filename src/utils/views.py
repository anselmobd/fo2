import base64
import hashlib
import re
import time
from pprint import pprint

from django.template.defaulttags import register

import base.models
from geral.functions import request_user

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
            tipo_imagem__slug=tipo,
            slug=imagem,
        )
        return image_to_data_url(imagem.imagem.path)
    except base.models.Imagem.DoesNotExist:
        return ''


def totalize_data(data, config):
    totrow = data[0].copy()
    for key in totrow.keys():
        totrow[key] = ''

    if 'row_style' in config:
        totrow['|STYLE'] = config['row_style']

    if 'class_suffix' in config:
        class_suffix = config['class_suffix']
        keys = [key for key in totrow.keys() if '|' not in key]
        for key in keys:
            totrow['{}|CLASS'.format(key)] = '{}{}'.format(key, class_suffix)

    sum = {key: 0 for key in config['sum']}
    for row in data:
        for key in sum:
            sum[key] += row[key]

    if 'descr' in config:
        for key in config['descr']:
            totrow[key] = config['descr'][key]

    for key in sum:
        totrow[key] = sum[key]

    if 'count' in config:
        for key in config['count']:
            totrow[key] = len(data)

    data.append(totrow)


def totalize_grouped_data(data, config):
    temp_end_row = data[0].copy()
    for key in temp_end_row:
        temp_end_row[key] = ''
    data.append(temp_end_row)

    if 'global_sum' in config:
        global_count = 0
        global_tot = temp_end_row.copy()
        if 'global_descr' not in config:
            config['global_descr'] = config['descr']
        for key in config['global_descr']:
            global_tot[key] = config['global_descr'][key]
        for key in config['global_sum']:
            global_tot[key] = 0

    for key in config['sum']:
        temp_end_row[key] = 0

    totrows = {}
    init_group = True
    for row_idx, row in enumerate(data):

        if not init_group:
            if list_key != [row[key] for key in config['group']]:
                for key in config['descr']:
                    totrow[key] = config['descr'][key]
                for key in sum:
                    totrow[key] = sum[key]
                for key in config['count']:
                    totrow[key] = group_count
                total = True
                if 'flags' in config and 'NO_TOT_1' in config['flags']:
                    total = group_count > 1
                if total:
                    totrows[row_idx] = totrow
                init_group = True

        if init_group:
            group_count = 0
            list_key = [row[key] for key in config['group']]
            totrow = row.copy()
            for key in totrow:
                if key not in config['group']:
                    totrow[key] = ''
            sum = {key: 0 for key in config['sum']}
            init_group = False

        for key in sum:
            sum[key] += row[key]
        group_count += 1

        if 'global_sum' in config:
            global_count += 1
            for key in config['global_sum']:
                global_tot[key] += row[key]

    for i in range(len(data)-1, 0, -1):
        if i in totrows:
            if 'row_style' in config:
                totrows[i]['|STYLE'] = config['row_style']
            data.insert(i, totrows[i])

    if 'global_sum' in config:
        total = True
        if 'flags' in config and 'NO_TOT_1' in config['flags']:
            total = global_count > 2  # por conta do temp_end_row
        if total:
            if 'row_style' in config:
                global_tot['|STYLE'] = config['row_style']
            data.insert(len(data)-1, global_tot)

    del(data[len(data)-1])


def group_rowspan(data, group):
    noSpan = True
    for i in range(len(data)):
        data[i]['rowspan'] = 1
    inferior = []
    atual = []
    for i in range(len(data)-1, -1, -1):
        atual = [data[i][f] for f in group]
        if atual == inferior:
            noSpan = False
            data[i]['rowspan'] = data[i]['rowspan'] + data[i+1]['rowspan']
            data[i+1]['rowspan'] = 0
        inferior = atual[:]
    if noSpan:
        del list(group)[:]


class TableDefs(object):
    '''
        formato do self.definition:
        {
            'field': {
                'header': 'Header',
                'style': 'text-align: right;',
            },
            ...
        }
    '''

    def __init__(self, definition, keys=None, **kwargs):
        '''
            se keys for uma lista de chaves como ['header', 'style'],
            a definition recebida estará no formato
            {
                'field': ['Header', 'text-align: right;'],
                ...
            }
            e deverá ser convertida para o formato do self.definition

            se uma key na lista de chaves iniciar com '+' como ['header', '+style'],
            valor do key será uma chave para um dicionário com esse nome
            passado no kwargs
        '''
        super(TableDefs, self).__init__()
        self.kwargs = kwargs
        self.cols_list = []
        if keys is None:
            self.definition = definition
        else:
            self.definition = self.convert(definition, keys)

    def convert(self, definition, keys):
        result = {}
        for col in definition:
            def_col = {}
            for i, key in enumerate(keys):
                if i < len(definition[col]):
                    if key.startswith('+'):
                        key = key[1:]
                        def_col[key] = self.kwargs[key][definition[col][i]]
                    else:
                        def_col[key] = definition[col][i]
            result[col] = def_col
        return result

    def cols(self, *cols):
        self.cols_list = cols

    def add(self, pos, *cols):
        if isinstance(pos, int):
            self.cols_list = self.cols_list[:pos] + cols + self.cols_list[pos:]
        else:
            self.cols_list += (pos,) + cols

    def defs(self, *cols):
        if len(cols) == 0:
            if len(self.cols_list) == 0:
                cols = self.definition.keys()
            else:
                cols = self.cols_list
        self.headers = []
        self.fields = []
        self.style = {}
        for idx, col in enumerate(cols, 1):
            if col in self.definition:
                self.headers.append(
                    self.definition[col].get('header', '') or col.capitalize())
                self.fields.append(col)
                if 'style' in self.definition[col]:
                    self.style[idx] = self.definition[col]['style']

    def hfs(self, *cols):
        self.defs(*cols)
        return self.headers, self.fields, self.style

    def hfs_dict(self, *cols):
        self.defs(*cols)
        return {
            'headers': self.headers,
            'fields': self.fields,
            'style': self.style,
        }


def hash_trail(*fields):
    hash_cache = ';'.join(map(format, fields))
    hash_object = hashlib.md5(hash_cache.encode())
    return hash_object.hexdigest()


def request_hash_trail(request, *fields):
    params = list(fields) + [
        time.strftime('%y%m%d'),
        request_user(request),
        request.session.session_key,
    ]
    return hash_trail(*params)


class TableHfs(TableDefs):

    def __init__(self, definition, keys=None, **kwargs):
        super(TableHfs, self).__init__(definition, keys, **kwargs)

import re
from pprint import pprint

from django.template.defaulttags import register

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
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)


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
                '<span style="opacity: 0.7;">',
                zeros,
                '</span>'])
    return text


@register.filter
def word_slice(text, slice):

    def adjust_cut(text, valor, limit=1):
        val = valor
        while text[val-1] != ' ' and val > 1:
            val -= 1
        if val <= limit:
            val = valor
        while text[val] == ' ' and val < len(text):
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


def totalize_data(data, config):
    totrow = data[0].copy()
    for key in totrow:
        totrow[key] = ''

    sum = {key: 0 for key in config['sum']}
    for row in data:
        for key in sum:
            sum[key] += row[key]

    for key in config['descr']:
        totrow[key] = config['descr'][key]

    for key in sum:
        totrow[key] = sum[key]

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

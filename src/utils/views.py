import re

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
                '<span style="opacity: 0.5;">',
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
        temp_end_row[key] = 0
    data.append(temp_end_row)

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
                if 'NO_TOT_1' not in config['flags'] or group_count > 1:
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

    for i in range(len(data)-1, 0, -1):
        if i in totrows:
            data.insert(i, totrows[i])
    del(data[len(data)-1])

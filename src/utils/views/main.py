import hashlib
import time
from pprint import pprint


from geral.functions import request_user


def totalize_data(data, config, return_not_append=False):
    if 'flags' in config and 'NO_TOT_1' in config['flags']:
        if len(data) < 2:
            return

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

    if return_not_append:
        return totrow
    else:
        data.append(totrow)


def get_total_row(data, config):
    return totalize_data(data, config, return_not_append=True)


def totalize_grouped_data(data, config):

    def copy_init_clean(row_ori, empty, not_fields, clean_pipe):
        row = row_ori.copy()
        del_keys = []
        for key in row:
            if key not in not_fields:
                row[key] = empty
            if clean_pipe:
                if '|' in key:
                    del_keys.append(key)
        for key in del_keys:
            del row[key]
        return row

    empty = config['empty'] if 'empty' in config else ''
    clean_pipe = config['clean_pipe'] if 'clean_pipe' in config else False

    temp_end_row = copy_init_clean(data[0], empty, [], clean_pipe)
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
                for key in config.get('count', []):
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
            totrow = copy_init_clean(row, empty, config['group'], clean_pipe)
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

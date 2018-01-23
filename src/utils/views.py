from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


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
    inicio = adjust_cut(text,  inicio)

    fim = int(slices[1]) if slices[1] != '' else len(text)
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

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

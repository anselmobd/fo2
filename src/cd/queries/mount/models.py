table = {
    'lp': {
        'table': "ENDR_014",
        'descr': "Lote/Palete",
        'field': {
            'palete': "COD_CONTAINER",
            'op': "ORDEM_PRODUCAO",
            'lote': "ORDEM_CONFECCAO",
            'data': "DATA_INCLUSAO",
        },
    },
    'op': {
        'table': "PCPC_020",
        'descr': "OP",
        'field': {
            'op': "ORDEM_PRODUCAO",
            'ref': "REFERENCIA_PECA",
            'pedido': "PEDIDO_VENDA",
        },
        'joined_to': {
            'lp': {
                'op': 'op'
            },
        },
    },
}

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
                'op': 'op',
                # 'op': ("       {}      --", 'op'),
            },
        },
    },
    'l_ref': {
        'table': "PCPC_040",
        'descr': "lote referência - sempre apenas o primeiro estágio",
        'field': {
            'op': "ORDEM_PRODUCAO",
            'oc': "ORDEM_CONFECCAO",
            'cor': "PROCONF_ITEM",
            'tam': "PROCONF_SUBGRUPO",
            'seq': "l.SEQUENCIA_ESTAGIO",
        },
        'condition': {
            'seq': (1, ),
        },
        'joined_to': {
            'lp': {
                'op': 'op',
                'oc': ("MOD({}, 100000)", 'lote'),
            },
        },
    },
}

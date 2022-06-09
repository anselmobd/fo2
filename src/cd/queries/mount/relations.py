from utils.functions import coalesce

from o2.queries.relations import Relations


class R(Relations):

    def __init__(self) -> None:
        super().__init__()

        self.table = {
            'lp': {
                'descr': "Lote/Palete",
                'table': "ENDR_014",
                'field': {
                    'palete': "COD_CONTAINER",
                    'op': "ORDEM_PRODUCAO",
                    'lote': "ORDEM_CONFECCAO",
                    'data': "DATA_INCLUSAO",
                },
                'joined_to': {
                    'l_ref': {
                        'op': self.F('op'),
                        'lote': ("{}*100000+{}", 'per', 'oc'),
                    },
                },
            },
            'sl': {
                'descr': "Solicitação/Lote",
                'table': "PCPC_044",
                'field': {
                    'sol': "SOLICITACAO",
                    'op': "ORDEM_PRODUCAO",
                    'oc': "ORDEM_CONFECCAO",
                    'qtd': "QTDE",
                    'ped_dest': "PEDIDO_DESTINO",
                    'ref_dest': "GRUPO_DESTINO",
                    'sit': "SITUACAO",
                },
                'make': {
                    'sol': (coalesce, '#'),
                },
                'condition': {
                    'oc': ['<>', 0],
                    # 'ref_dest': ['NOT IN', ("('0', '00000')", )],
                },
                'joined_to': {
                    'lp': {
                        'op': 'op',
                        'oc': ("MOD({}, 100000)", 'lote'),
                    },
                },
            },
            'op': {
                'descr': "OP",
                'table': "PCPC_020",
                'field': {
                    'op': "ORDEM_PRODUCAO",
                    'ref': "REFERENCIA_PECA",
                    'pedido': "PEDIDO_VENDA",
                },
                'joined_to': {
                    'lp': {
                        'op': 'op',
                    },
                    'sl': {
                        'op': 'op',
                    },
                },
            },
            'l_ref': {
                'descr': "lote de referência - sempre apenas o primeiro estágio",
                'table': "PCPC_040",
                'field': {
                    'op': "ORDEM_PRODUCAO",
                    'per': "PERIODO_PRODUCAO",
                    'oc': "ORDEM_CONFECCAO",
                    'cor': "PROCONF_ITEM",
                    'tam': "PROCONF_SUBGRUPO",
                    'seq': "SEQUENCIA_ESTAGIO",
                    'qtd_lote': "QTDE_PECAS_PROG",
                },
                'condition': {
                    'seq': 1,
                },
                'joined_to': {
                    'lp': {
                        'op': 'op',
                        'oc': ("MOD({}, 100000)", 'lote'),
                    },
                },
            },
            'l_63': {
                'descr': "lote no 63 - sempre apenas o estágio 63 (se houver)",
                'table': "PCPC_040",
                'field': {
                    'op': "ORDEM_PRODUCAO",
                    'per': "PERIODO_PRODUCAO",
                    'oc': "ORDEM_CONFECCAO",
                    'cor': "PROCONF_ITEM",
                    'ref': "PROCONF_GRUPO",
                    'tam': "PROCONF_SUBGRUPO",
                    'seq': "SEQUENCIA_ESTAGIO",
                    'qtd_lote': "QTDE_PECAS_PROG",
                    'est': "CODIGO_ESTAGIO",
                    'qtd': "QTDE_DISPONIVEL_BAIXA",
                },
                'condition': {
                    'est': 63,
                },
                'joined_to': {
                    'lp': {
                        'op': 'op',
                        'oc': ("MOD({}, 100000)", 'lote'),
                    },
                    'sl': {
                        'op': 'op',
                        'oc': 'oc',
                    },
                },
            },
        }

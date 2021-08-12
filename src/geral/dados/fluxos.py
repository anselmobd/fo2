from pprint import pprint

from utils.functions.dict import update_dict

from geral.dados.alternativas import dict_alternativas
from geral.dados.roteiros import dict_roteiros
from geral.dados.estagios import dict_estagios


def dict_fluxo(id):
    try:
        id = int(id)
        fluxo_num = int(id)
    except Exception:
        fluxo_num = int(id[:-1])

    alternativas = dict_alternativas()
    roteiros = dict_roteiros()
    estagios = dict_estagios()

    fluxo_base = {
        # gerais
        'alternativas': alternativas,
        'roteiros': roteiros,
        'estagios': estagios,
        # templates
        'template_bloco': 'geral/fluxo_bloco.html',
        # específicos
        # 'rascunho': '#Rascunho#',
        'rascunho': '',
        'versao_num': '21.01',
        'versao_data': '02/03/2021',
        'versao_sufixo': '20210302',
        'id': id,
        'fluxo_num': fluxo_num,
    }

    fluxo_padrao = {}

    fluxo_padrao['cueca'] = fluxo_base.copy()
    fluxo_padrao['cueca'].update({
        # templates
        'template_base': 'geral/fluxo.html',
        # específicos
        'tem_mp': False,
        'seta_md_label': 'MD',
        'seta_pg_label': 'PG / PB',
        'seta_pa_label': 'PA',
        'md_cabecalho': 'MD\nDepósito da OP: 231',
        'md_p_pb': {
            'nivel': 'md',
            'alt_incr': 0,
            'nome': 'mdpb',
            'cabecalho': 'MD p/ PB - <b><u>M</u></b>999*<br />'
                         'Com acessórios (TAG)<br />para encabidar',
        },
        'md_p_pg': {
            'nivel': 'md',
            'alt_incr': 0,
            'nome': 'mdpg',
            'cabecalho': 'MD p/ PG - <b><u>M</u></b>999<b><u>A</u></b><br />'
                         'Sem acessórios (TAG)<br />para encabidar',
        },
        'mdext1': False,
        'mdext2': False,
        'pb': {
            'nivel': 'pb',
            'alt_incr': 10,
            'nome': 'pb1x',
            'cabecalho': 'PB - <b><u>B</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Individual Encabidado',
        },
        'pg': {
            'nivel': 'pg',
            'alt_incr': 20,
            'nome': 'pg2x',
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Kit ou<br />Individual Encabidado ou<br />'
                         'Individual Embalado',
        },
        'pa_cabecalho': 'PA - 9999*\nDepósito da OP: 101/102',
        'pa_de_md': {
            'nivel': 'pa',
            'alt_incr': 0,
            'nome': 'pa0x',
            'cabecalho': 'Kit ou<br />Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
        },
        'pa_enc_de_pb': {
            'nivel': 'pa',
            'alt_incr': 10,
            'nome': 'pa1x',
            'cabecalho': 'Individual Encabidado',
        },
        'pa_emb_de_pg': {
            'nivel': 'pa',
            'alt_incr': 20,
            'nome': 'pa2x',
            'cabecalho': 'Kit ou<br />Individual Embalado',
        },
        'pa_enc_de_pg': {
            'nivel': 'pa',
            'alt_incr': 30,
            'nome': 'pa3x',
            'cabecalho': 'Individual Emcabidado',
        },
    })

    fluxo_padrao['1_bloco'] = fluxo_base.copy()
    fluxo_padrao['1_bloco'].update({
        # templates
        'template_base': 'geral/fluxo_com_1_bloco.html',
        # específicos
        'bloco': {
            'alt_incr': 0,
            'nome': 'bloco',
        },
    })

    fluxo_config = {}

    fluxo_config[1] = {
        'base': 'cueca',
        'fluxo_nome': 'Interno',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Interna',
        ],
        'md_p_pb': {
            'ests': [3, 6, 12, 15, 18, 21, 33, 45, 48, 51],
            'gargalo': 33,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Elástico',
                     'TAG',
                     'Transfer', ],
            },
        },
        'md_p_pg': {
            'ests': [3, 6, 12, 15, 18, 21, 33, 45, 48, 51],
            'gargalo': 33,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Elástico',
                     'Transfer', ],
            },
        },
        'pb': {
            'ests': [3, 18, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: ['Cabide', ],
                60: ['MD p/ PB<br /><b><u>M</u></b>999*', ],
            },
        },
        'pg': {
            'ests': [3, 18, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                60: ['MD p/ PG<br /><b><u>M</u></b>999<b><u>A</u></b>', ],
            },
        },
        'pa_de_md': {
            'ests': [3, 18, 60, 57, 63, 66],
            'gargalo': 60,
            'insumos': {
                18: [
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                60: ['MD<br /><b><u>M</u></b>999*'],
            }
        },
        'pa_enc_de_pb': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_emb_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'TAG',
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
    }

    # 1p
    fluxo_aux = {
        'produto': 'SHORT',
        'caracteristicas': [
            'Corte: Interno',
            'Estamparia: Interna ou Sem',
            'Costura: Interna',
        ],
        'seta_pg_label': 'PG',
        'tem_mp': True,
        'md_p_pb': False,
        'mp_cabecalho': 'Tela - F9999\nFluxo 8p',
        'md_p_pg': {
            'cabecalho': 'MD - <b><u>M</u></b>999*',
            'ests': [3, 6, 12, 15, 43, 18, 21, 32, 33, 45, 48, 51],
            'insumos': {
                15: ['Tela',
                     'Malha', ],
                18: ['Etiquetas',
                     'Elástico',
                     'Cadarço', ],
            },
        },
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231',
            'insumos': {
                18: ['TAG', ],
                60: ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'pa_de_md': {
            'cabecalho': 'Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
            'insumos': {
                18: [
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'Individual Embalado',
            'insumos': {
                18: [
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_enc_de_pg': {
            'insumos': {
                18: [
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
    }
    fluxo_config['1p'] = update_dict(fluxo_config[1], fluxo_aux)

    fluxo_config[2] = {
        'base': 'cueca',
        'fluxo_nome': 'Costura externa',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'cabecalho': 'MD p/ PB - <b><u>C</u></b>999*<br />'
                         'Com acessórios (TAG)<br />para encabidar',
            'ests': [3, 6, 12, 15, 18],
            'gargalo': 12,
            'insumos': {
                15: ['Malha', ],
            },
        },
        'md_p_pg': {
            'cabecalho': 'MD p/ PG - <b><u>C</u></b>999<b><u>A</u></b><br />'
                         'Sem acessórios (TAG)<br />para encabidar',
            'ests': [3, 6, 12, 15, 18],
            'gargalo': 12,
            'insumos': {
                15: ['Malha', ],
            },
        },
        'pb': {
            'ests': [3, 18, 21, 'os', 24, 55, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD p/ PB<br /><b><u>C</u></b>999*'],
                55: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Cabide',
                ],
            }
        },
        'pg': {
            'ests': [3, 18, 21, 'os', 24, 55, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD p/ PG<br /><b><u>C</u></b>999<b><u>A</u></b>'],
                55: [
                    'Etiquetas',
                    'Elástico',
                ],
            }
        },
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 55, 57, 63, 66],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                'os': ['MD<br /><b><u>C</u></b>999*'],
                55: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Transfer',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                ],
            }
        },
        'pa_enc_de_pb': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_emb_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'TAG',
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
    }

    # 2p <- 2
    fluxo_aux = {
        'produto': 'SHORT',
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>C</u></b>999*',
            'insumos': {
                15: ['Forro',
                     'Malha', ],
            },
        },
        'md_p_pg': False,
        'pb': False,
        'pg': False,
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63, 66],
            'insumos': {
                54: [
                    'Etiquetas',
                    'Elástico',
                    'Ilhós',
                    'Transfer',
                    'Cabide',
                    'Embalagem',
                ],
                55: [],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': False,
        'pa_enc_de_pg': False,
    }
    fluxo_config['2p'] = update_dict(fluxo_config[2], fluxo_aux)

    fluxo_config[3] = {
        'base': 'cueca',
        'fluxo_nome': 'Corte e costura externos',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Externo',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>R</u></b>999*',
            'ests': [3, 6, 12],
            'gargalo': 12,
        },
        'md_p_pg': False,
        'pb': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD<br /><b><u>R</u></b>999*', ],
                57: [
                    'Malha',
                    'Etiquetas',
                    'Elástico',
                    'Transfer',
                    'TAG',
                    'Cabide',
                ],
            },
        },
        'pg': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD<br /><b><u>R</u></b>999*', ],
                57: [
                    'Malha',
                    'Etiquetas',
                    'Elástico',
                    'Transfer',
                ],
            },
        },
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63, 66],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                'os': ['MD<br /><b><u>R</u></b>999*'],
                54: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                ],
            }
        },
        'pa_enc_de_pb': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_emb_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': False,
    }

    fluxo_config[4] = fluxo_config[1].copy()
    fluxo_config[4].update({
        'fluxo_nome': 'Tecelagem de cueca',
        'produto': 'CUECA SEM costura',
        'caracteristicas': [
            'Tecelagem: Interna',
            'Costura: Interna',
            'Tingimento: Externo',
        ],
        'tem_mp': False,
        'md_p_pb': {
            'ests': [3, 22, 9, 27, 30, 36, 21, 'os', 24, 39, 18, 45, 48, 51],
            'gargalo': 27,
            'insumos': {
                27: ['Fio', ],
                15: ['Malha', ],
                18: ['Etiquetas',
                     'TAG',
                     'Transfer', ],
            },
        },
        'md_p_pg': {
            'ests': [3, 22, 9, 27, 30, 36, 21, 'os', 24, 39, 18, 45, 48, 51],
            'gargalo': 27,
            'insumos': {
                27: ['Fio', ],
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Transfer', ],
            },
        },
    })

    # 5 <- 1
    fluxo_aux = {
        'fluxo_nome': 'Costura externa de sunga',
        'produto': 'SUNGA',
        'caracteristicas': [
            'Corte: Interno',
            'Estamparia: Interna ou Sem',
            'Costura: Externa',
        ],
        'seta_pg_label': 'PG',
        'tem_mp': True,
        'mp_cabecalho': 'Forro - F9999\nFluxo 8',
        'md_p_pb': False,
        'md_p_pg': {
            'cabecalho': 'MD - <b><u>C</u></b>999*',
            'ests': [3, 6, 12, 15, 18, 21, 'os', 24, 55, 45, 51],
            'gargalo': 24,
            'insumos': {
                15: ['Malha', ],
                18: ['Transfer', ],
                55: ['Etiquetas',
                     'Forro - <b><u>F</u></b>999*',
                     'Eslástico',
                     'Cadarço', ],
            },
        },
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231',
            'insumos': {
                18: ['TAG', ],
                60: ['MD<br /><b><u>C</u></b>999*', ],
            },
        },
        'pa_cabecalho': 'PA\nDepósito da OP: 101/102',
        'pa_de_md': {
            'cabecalho': 'PA - 9999*<br /><br />'
                         'Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
            'insumos': {
                18: [
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
                60: ['MD<br /><b><u>C</u></b>999*'],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'PA - 9999<b><u>A</u></b><br /><br />'
                         'Individual Embalado',
            'insumos': {
                18: [
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_enc_de_pg': {
            'cabecalho': 'PA - 99999<br /><br />'
                         'Individual Encabidado',
            'insumos': {
                18: [
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
    }
    fluxo_config[5] = update_dict(fluxo_config[1], fluxo_aux)

    # 53 <- 5
    fluxo_aux = {
        'fluxo_nome': 'Costura externa de MD',
        'produto': 'Vários',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Externa',
            'Embalagem: Interna',
        ],
        'tem_mp': False,
        'md_p_pg': {
            'insumos': {
                15: ['Malha', ],
                18: ['Transfer', ],
                55: ['Etiquetas',
                     'Eslástico',
                     'Cadarço', ],
            },
        },
    }
    fluxo_config[53] = update_dict(fluxo_config[5], fluxo_aux)

    fluxo_config[6] = {
        'base': '1_bloco',
        'fluxo_nome': 'Costura externa de camisa',
        'produto': 'CAMISA',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Externa',
        ],
        'seta_label': 'MD',
        'bloco': {
            'nivel': 'md',
            'cabecalho': 'MD - x9999<br />'
                         'Depósito da OP: 231',
            'ests': [3, 6, 12, 15, 18, 21, 'os', 24, 55, 45, 51],
            'gargalo': 24,
            'insumos': {
                15: ['Malha', ],
                18: ['Transfer', ],
                55: ['Etiquetas', ],
            },
        },
    }

    fluxo_config[7] = {
        'base': 'cueca',
        'fluxo_nome': 'Pijama',
        'produto': 'PIJAMA',
        'caracteristicas': [],
        'seta_pg_label': 'PG',
        'md_p_pb': False,
        'md_p_pg': False,
        'mdext1':  {
            'cabecalho': 'MD SAMBA - <b><u>M</u></b>999*<br />Fluxo 1',
        },
        'mdext2':  {
            'cabecalho': 'MD CAMISA - <b><u>M</u></b>999*<br />Fluxo 6',
        },
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Kit',
            'ests': [3, 18, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                ],
                60: [
                    'MD SAMBA<br /><b><u>M</u></b>999*',
                    'MD CAMISA<br /><b><u>M</u></b>999*',
                ],
            },
        },
        'pa_de_md': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 60, 57, 63, 66],
            'gargalo': 60,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                60: [
                    'MD SAMBA<br /><b><u>M</u></b>999*',
                    'MD CAMISA<br /><b><u>M</u></b>999*',
                ],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': False,
    }

    fluxo_config[8] = {
        'base': '1_bloco',
        'fluxo_nome': 'Parte cortada',
        'produto': 'SUNGA (Forro)',
        'caracteristicas': [
            'Corte: Interno',
        ],
        'seta_label': 'MP',
        'bloco': {
            'nivel': 'mp',
            'cabecalho': 'MP - <b><u>F</u></b>9999<br />'
                         'Depósito da OP: 231',
            'ests': [3, 6, 15],
            'gargalo': 6,
            'insumos': {
                15: ['Malha', ],
            },
        },
    }

    # 8p <- 8
    fluxo_aux = {
        'fluxo_nome': 'Parte preparada',
        'produto': 'SHORT (tela)',
        'bloco': {
            'nivel': 'mp',
            'cabecalho': 'MP - <b><u>F</u></b>9999<br />'
                         'Depósito da OP: 231',
            'ests': [3, 6, 15, 18, 21, 31],
            'gargalo': 6,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas', ],
            },
        },
    }
    fluxo_config['8p'] = update_dict(fluxo_config[8], fluxo_aux)

    fluxo_config[9] = {
        'base': 'cueca',
        'produto': 'MEIA',
        'fluxo_nome': 'Tecelagem de meia',
        'caracteristicas': [
            'Tecelagem: Interna',
        ],
        'seta_pg_label': 'PG',
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>M</u></b>999*<br />'
                         'Depósito da OP: 231',
            'ests': [3, 22, 9, 27, 28, 51],
            'gargalo': 27,
            'insumos': {
                27: ['Fio', ],
            },
        },
        'md_p_pg': False,
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Kit',
            'ests': [3, 18, 60, 48, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: ['Etiquetas',
                     'TAG', ],
                60: ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'pa_de_md': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 60, 48, 57, 63, 66],
            'gargalo': 60,
            'insumos': {
                18: ['Etiquetas',
                     'TAG', ],
                60: ['MD<br /><b><u>M</u></b>999*'],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': False,
    }

    # 51
    fluxo_aux = {
        'produto': 'Não Tecelagem',
    }
    aux_blocos = [
        'md_p_pb', 'md_p_pg', 'pb', 'pg', 'pa_de_md', 'pa_enc_de_pb',
        'pa_emb_de_pg', 'pa_enc_de_pg',
    ]
    for aux_bloco in aux_blocos:
        fluxo_aux[aux_bloco] = {
            'ests': [e if e != 18 else 19
                     for e in fluxo_config[1][aux_bloco]['ests']],
            'insumos': {
                18: [],
                19: (fluxo_config[1][aux_bloco]['insumos'][18]
                     if 18 in fluxo_config[1][aux_bloco]['insumos'] else [])
            },
        }
    fluxo_config[51] = update_dict(fluxo_config[1], fluxo_aux)

    # 51p
    fluxo_aux = {
        'produto': 'SUNGA - SHORT',
        'tem_mp': True,
    }
    aux_blocos = [
        'pg', 'pa_emb_de_pg', 'pa_enc_de_pg',
    ]
    for aux_bloco in aux_blocos:
        if fluxo_config[5][aux_bloco]:
            fluxo_aux[aux_bloco] = {
                'ests': [e if e != 18 else 19
                         for e in fluxo_config['1p'][aux_bloco]['ests']],
                'insumos': {
                    18: [],
                    19: (fluxo_config['1p'][aux_bloco]['insumos'][18]
                         if 18 in fluxo_config['1p'][aux_bloco]['insumos']
                         else [])
                },
            }
    fluxo_config['51p'] = update_dict(fluxo_config['1p'], fluxo_aux)

    fluxo_config['51p']['pa_emb_de_pg']['cabecalho'] = (
        'PA - 9999<b><u>A</u></b><br /><br />'
        'Individual Embalado')
    fluxo_config['51p']['pa_enc_de_pg']['cabecalho'] = (
        'PA - 99999<br /><br />'
        'Individual Encabidado')

    fluxo_config[52] = {
        'base': 'cueca',
        'produto': 'MULTIMARCA',
        'fluxo_nome': 'Sobra de multimarca',
        'caracteristicas': [],
        'seta_md_label': 'PPG',
        'seta_pa_label': 'PG',
        'md_cabecalho': 'PPG\nDepósito da OP: 231',
        'md_p_pb': {
            'cabecalho': '<b><u>D</u></b>999* - para Desmontar',
            'ests': [3, 57, 63],
            'gargalo': 57,
            'insumos': {
                57: ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'md_p_pg': False,
        'pb': False,
        'pg': False,
        'pa_cabecalho': 'PG\nDepósito da OP: 231',
        'pa_de_md': {
            'cabecalho': '<b><u>A</u></b>999* - Remontado',
            'ests': [3, 18, 45, 48, 51, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: ['Cartela',
                     'Transfer',
                     'Etiquetas',
                     'TAG', ],
                60: ['PPG<br /><b><u>D</u></b>999*'],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': False,
        'pa_enc_de_pg': False,
    }

    if id not in fluxo_config:
        return None

    return update_dict(
        fluxo_padrao[fluxo_config[id]['base']], fluxo_config[id])

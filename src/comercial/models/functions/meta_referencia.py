import numpy as np
from pprint import pprint

from django.urls import reverse

from utils.functions.strings import join_non_empty

import produto.queries

import comercial.models
import comercial.queries


def descr_combinacoes_de_alternativas(cursor, ref):
    ref_alternativas = produto.queries.ref_estruturas(cursor, ref)
    alternativas = list(set([alt['ALTERNATIVA'] for alt in ref_alternativas]))

    comb_info = {
        'cores_list': [],
    }
    for alternativa in alternativas:
        cores_dict_alt = produto.queries.dict_combinacoes_cores(
            cursor, ref, alternativa)

        cores_list = []

        for cor in cores_dict_alt:
            conta = cores_dict_alt[cor]
            cor1_list = [
                f"{conta[item]} {item}"
                for item in conta
            ]
            cor1 = ' + '.join(cor1_list)
            cores_list.append(f"{cor} = {cor1}")

        comb_info['cores_list'].append(cores_list)
    comb_info['cores_dict'] = cores_dict_alt

    conta_componentes = 0
    for cor in cores_dict_alt:
        for comp in cores_dict_alt[cor]:
            conta_componentes += cores_dict_alt[cor][comp]
        break
    comb_info['conta_componentes'] = conta_componentes
    return comb_info


def critica_cores_list(comb_cores_list):
    len_alt_cores = 0
    len_alt_cores_err = False
    for alt_cores in comb_cores_list:
        if len_alt_cores == 0:
            len_alt_cores = len(alt_cores)
        else:
            len_alt_cores_err = len_alt_cores_err or len_alt_cores != len(alt_cores)

    if len_alt_cores_err:
        ok = False
        info = 'ERRO: Alternativas com número de cores diferentes'
    else:
        ok = True
        alt_cores_arr = np.array(comb_cores_list)
        alt_cores_arr_t = alt_cores_arr.transpose()
        cores_ok = []
        cores_err = []
        for alt_cores_vet in alt_cores_arr_t:
            alt_cores_set = list(set(alt_cores_vet))
            if len(alt_cores_set) == 1:
                cores_ok.append(alt_cores_set[0])
            else:
                cores_err.append(alt_cores_set)

        info = ''
        if len(cores_err) != 0:
            ok = False
            info = ' ERRO: '
            for cor_err in cores_err:
                info += ' DIFERE DE '.join(cor_err)
        info += join_non_empty(
            '; ',
            [info, '; '.join(cores_ok)]
        )
    return ok, info


def meta_ref_incluir(cursor, modelo):
    """Referências a incluir no cálculo de definição de meta
    """
    ref_incl = comercial.models.MetaModeloReferencia.objects.filter(
        modelo=modelo,
        incl_excl='i',
    ).order_by('referencia').values('referencia')
    if len(ref_incl) != 0:

        for ref in ref_incl:
            ref['modelo'] = ''.join(i for i in ref['referencia'] if i.isdigit())
            ref['modelo'] = ref['modelo'].lstrip('0')
            ref['referencia|TARGET'] = '_blank'
            ref['referencia|LINK'] = reverse(
                'produto:ref__get',
                args=[ref['referencia']],
            )

            comb_info = descr_combinacoes_de_alternativas(
                    cursor, ref['referencia'])
            ref['cores_dict'] = comb_info['cores_dict']
            ref['conta_componentes'] = comb_info['conta_componentes']

            ref['ok'], ref['info'] = critica_cores_list(
                comb_info['cores_list'])

    return ref_incl

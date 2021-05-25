import numpy as np
from pprint import pprint

from django.urls import reverse

from utils.functions.strings import join_non_empty

import produto.queries

import comercial.models
import comercial.queries


def meta_ref_incluir(cursor, context, modelo):
    # referências a incluir
    ref_incl = comercial.models.MetaModeloReferencia.objects.filter(
        modelo=modelo,
        incl_excl='i',
    ).order_by('referencia').values('referencia')
    if len(ref_incl) != 0:

        for ref in ref_incl:
            ref['referencia|TARGET'] = '_blank'
            ref['referencia|LINK'] = reverse(
                'produto:ref__get',
                args=[ref['referencia']],
            )

            alternativas = produto.queries.ref_estruturas(
                cursor, ref['referencia'])
            alternativas = list(set([alt['ALTERNATIVA'] for alt in alternativas]))

            alt_cores_list = []
            for alternativa in alternativas:
                estrutura = produto.queries.combinacoes_cores(
                    cursor, ref['referencia'], alternativa)

                alt_cores = {}
                for row in estrutura:
                    cor_item = row['COR_ITEM'].lstrip("0")
                    cor_comp = row['COR_COMP'].lstrip("0")
                    try:
                        alt_cor = alt_cores[cor_item]
                    except KeyError:
                        alt_cores[cor_item] = {}
                        alt_cor = alt_cores[cor_item]
                    try:
                        alt_cor[cor_comp] += row['CONSUMO']
                    except KeyError:
                        alt_cor[cor_comp] = row['CONSUMO']

                cores_list = []
                for cor in alt_cores:
                    conta = alt_cores[cor]
                    cor1_list = [
                        f"{conta[item]} {item}"
                        for item in conta
                    ]
                    cor1 = ' + '.join(cor1_list)
                    cores_list.append(f"{cor} = {cor1}")


                alt_cores_list.append(cores_list)

            len_alt_cores = 0
            len_alt_cores_err = False
            for alt_cores in alt_cores_list:
                if len_alt_cores == 0:
                    len_alt_cores = len(alt_cores)
                else:
                    len_alt_cores_err = len_alt_cores_err or len_alt_cores != len(alt_cores)

            if len_alt_cores_err:
                ref['info'] = 'ERRO: Alternativas com número de cores diferentes'
            else:
                alt_cores_arr = np.array(alt_cores_list)
                alt_cores_arr_t = alt_cores_arr.transpose()
                cores_ok = []
                cores_err = []
                for alt_cores_vet in alt_cores_arr_t:
                    alt_cores_set = list(set(alt_cores_vet))
                    if len(alt_cores_set) == 1:
                        cores_ok.append(alt_cores_set[0])
                    else:
                        cores_err.append(alt_cores_set)

                ref['info'] = ''
                if len(cores_err) != 0:
                    ref['info'] = ' ERRO: '
                    for cor_err in cores_err:
                        ref['info'] += ' DIFERE DE '.join(cor_err)
                ref['info'] += join_non_empty(
                    '; ',
                    [ref['info'], '; '.join(cores_ok)]
                )

    return True, ref_incl

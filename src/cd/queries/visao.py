from pprint import pprint

from django.urls import reverse

from utils.functions.digits import fo2_digit_with

import lotes.models


def get_solic_dict(rua):
    solicitacoes = lotes.models.SolicitaLoteQtd.objects.filter(
        lote__local__startswith=rua
    ).exclude(
        lote__local__isnull=True
    ).exclude(
        lote__local__exact=''
    ).values(
        'lote__local', 'solicitacao__id', 'solicitacao__data'
    ).distinct().order_by(
        'lote__local'
    )

    solic_dict = {}
    for solic in solicitacoes:

        solic_lote = solic['lote__local']

        solic_dt_entrega = solic['solicitacao__data']
        if solic_dt_entrega:
            solic_dt_entrega = f'({solic_dt_entrega:%d/%m/%y})'
        else:
            solic_dt_entrega = ''

        solic_id = solic['solicitacao__id']
        solic_numero = fo2_digit_with(solic_id)
        solic_txt = f"#{solic_numero}{solic_dt_entrega}"
        solicit_num_link = reverse(
            'cd:solicitacoes', args=[solic_id])

        solicit_html = (
            f'<a href="{solicit_num_link}" '
            f'target="_BLANK">{solic_txt}</a>'
        )

        if solic_lote not in solic_dict:
            solic_dict[solic_lote] = []
        
        solic_dict[solic_lote].append(solicit_html)
    return solic_dict

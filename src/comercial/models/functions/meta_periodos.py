from datetime import datetime
from pprint import pprint

from utils.functions import dec_month, dec_months

import comercial.models
import comercial.queries


def get_meta_periodos():
    data_nfs = list(comercial.models.ModeloPassadoPeriodo.objects.filter(
        modelo_id=1).order_by('ordem').values())
    if len(data_nfs) == 0:
        raise Exception('Nenhum período definido para análise de meta')

    periodos = []
    periodos_headers = []
    periodos_fields = []
    periodos_col_fields = []
    periodo_cols = {}
    periodos_zero_data_row = {}
    periodos_zero_field_row = {}
    style_meses = {}
    tot_peso = 0
    n_mes = 0
    hoje = datetime.today()
    mes = dec_month(hoje, 1)
    for i, row in enumerate(data_nfs):
        meses = row['meses']
        peso = row['peso']
        range_str = f"{n_mes + meses}:{n_mes}"
        field = comercial.queries.str2col_name(range_str)
        periodo = {
            'field': field,
            'range': range_str,
            'meses': meses,
            'peso': peso,
        }
        n_mes += meses
        tot_peso += meses * peso

        mes_fim = mes.strftime("%m/%Y")
        mes = dec_months(mes, meses-1)
        mes_ini = mes.strftime("%m/%Y")
        mes = dec_month(mes)
        if meses == 1:
            periodo_descr = mes_ini
        else:
            if mes_ini[-4:] == mes_fim[-4:]:
                periodo_descr = '{} - {}'.format(mes_fim[:2], mes_ini)
            else:
                periodo_descr = '{} - {}'.format(mes_fim, mes_ini)

        periodos.append(periodo)
        periodos_headers.append(
            '{} (P:{})'.format(periodo_descr, peso)
        )
        periodos_fields.append(range_str)
        periodos_col_fields.append(field)
        periodo_cols[field] = range_str
        periodos_zero_data_row[range_str] = 0
        periodos_zero_field_row[field] = 0

        # por padrão, meses ficam nas colunas 2 em diante
        style_meses[i+2] = 'text-align: right;'

    return {
        'list': periodos,
        'headers': periodos_headers,
        'fields': periodos_fields,
        'col_fields': periodos_col_fields,
        'cols': periodo_cols,
        'zero_data_row': periodos_zero_data_row,
        'zero_field_row': periodos_zero_field_row,
        'style_meses': style_meses,
        'tot_peso': tot_peso,
        'n_periodos': len(periodos),
    }

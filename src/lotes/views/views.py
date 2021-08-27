from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django_tables2 import RequestConfig

from fo2.connections import db_cursor_so

from utils.functions.models import rows_to_dict_list
from geral.functions import get_empresa

import lotes.models as models
import lotes.forms as forms
from lotes.tables import ImpressoraTermicaTable


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'lotes/index_agator.html')
    else:
        return render(request, 'lotes/index.html')


def impressoraTermica(request):
    table = ImpressoraTermicaTable(
        models.ImpressoraTermica.objects.all())
    RequestConfig(request, paginate=False).configure(
        table)
    return render(
        request, 'lotes/impressora_termica.html',
        {'impressora_termica': table,
         'titulo': 'Impressora Térmica',
         })


# OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD


def posicaoOri(request):
    context = {}
    if request.method == 'POST':
        form = forms.LoteForm(request.POST)
        if form.is_valid():
            lote = form.cleaned_data['lote']
            periodo = lote[:4]
            ordem_confeccao = lote[-5:]
            cursor = db_cursor_so(request)
            sql = '''
                SELECT
                  CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE = 0 THEN 0
                  ELSE l.CODIGO_ESTAGIO
                  END CODIGO_ESTAGIO
                , CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE = 0 THEN 'FINALIZADO'
                  ELSE e.DESCRICAO
                  END DESCRICAO_ESTAGIO
                FROM PCPC_040 l
                JOIN MQOP_005 e
                  ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
                WHERE l.PERIODO_PRODUCAO = %s
                  AND l.ORDEM_CONFECCAO = %s
                  AND l.SEQ_OPERACAO =
                  (
                    SELECT
                      max(lms.SEQ_OPERACAO)
                    FROM PCPC_040 lms
                    WHERE lms.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND lms.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                      AND lms.QTDE_EM_PRODUCAO_PACOTE =
                          lms.QTDE_A_PRODUZIR_PACOTE
                  )
            '''
            cursor.execute(sql, [periodo, ordem_confeccao])
            data = rows_to_dict_list(cursor)
            if len(data) == 0:
                context = {
                    'lote': lote,
                    'codigo_estagio': 'X',
                    'descricao_estagio': 'LOTE NÃO ENCONTRADO',
                }
            else:
                row = data[0]
                context = {
                    'lote': lote,
                    'codigo_estagio': row['CODIGO_ESTAGIO'],
                    'descricao_estagio': row['DESCRICAO_ESTAGIO'],
                }
    else:
        form = forms.LoteForm()
    context['form'] = form
    return render(request, 'lotes/posicaoOri.html', context)

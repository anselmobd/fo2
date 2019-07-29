from pprint import pprint

from django.db import connections
from django.db.models import Exists, OuterRef
from django.http import JsonResponse

from utils.views import totalize_data
from base.views import O2BaseGetView, O2BaseGetPostView

import comercial.models
from comercial.views.estoque import grade_meta_estoque
import comercial.forms
import produto.queries
import produto.models

import lotes.models
from lotes.views.quant_estagio import grade_meta_giro


class AProduzir(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(AProduzir, self).__init__(*args, **kwargs)
        self.template_name = 'lotes/a_produzir.html'
        self.title_name = 'A produzir por modelo'

    def mount_context(self):
        cursor = connections['so'].cursor()

        data = []

        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False)
        metas = metas.exclude(venda_mensal=0)
        metas = metas.values()

        for row in metas:
            data_row = next(
                (dr for dr in data if dr['modelo'] == row['modelo']),
                False)
            if not data_row:
                data_row = {
                    'modelo': row['modelo'],
                }
                data.append(data_row)
            data_row['meta_giro'] = row['meta_giro']
            data_row['meta_estoque'] = row['meta_estoque']
            data_row['meta'] = row['meta_giro'] + row['meta_estoque']
            data_row['total_op'] = 0
            data_row['total_op|CLASS'] = 'total_op-{}'.format(row['modelo'])
            data_row['total_ped'] = 0
            data_row['total_ped|CLASS'] = 'total_ped-{}'.format(row['modelo'])
            data_row['op_menos_ped'] = 0
            data_row['op_menos_ped|CLASS'] = 'op_menos_ped-{}'.format(
                row['modelo'])
            data_row['a_produzir'] = data_row['meta']
            data_row['a_produzir|CLASS'] = 'a_produzir-{}'.format(
                row['modelo'])
            data_row['excesso'] = 0
            data_row['excesso|CLASS'] = 'excesso-{}'.format(
                row['modelo'])

        data = sorted(data, key=lambda i: -i['meta'])

        totalize_data(data, {
            'sum': ['meta_giro', 'meta_estoque', 'meta', 'total_op',
                    'total_ped', 'op_menos_ped', 'a_produzir', 'excesso'],
            'count': [],
            'descr': {'modelo': 'Totais:'},
            'row_style': 'font-weight: bold;',
            'class_suffix': '__total',
        })

        self.context.update({
            'headers': ['Modelo', 'Meta de estoque', 'Meta de giro (lead)',
                        'Total das metas (A)', 'Total das OPs',
                        'Carteira de pedidos', 'OPs – Pedidos (B)',
                        'A produzir (A-B)[+]', 'Excesso (A-B)[-]'],
            'fields': ['modelo', 'meta_estoque', 'meta_giro',
                       'meta', 'total_op',
                       'total_ped', 'op_menos_ped',
                       'a_produzir', 'excesso'],
            'data': data,
            'style': {
                2: 'text-align: right;',
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
            },
        })


def op_producao_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        data_op = lotes.models.busca_op(
            cursor, modelo=modelo, tipo='v', tipo_alt='p',
            situacao='a', posicao='p')

        if len(data_op) == 0:
            total_op = 0
        else:
            totalize_data(data_op, {
                'sum': ['QTD_AP'],
                'count': [],
                'descr': {'OP': 'T:'},
            })
            total_op = data_op[-1]['QTD_AP']

    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar OP',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'total_op': total_op,
    })
    return JsonResponse(data, safe=False)


def pedido_lead_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        colecao = produto.queries.colecao_de_modelo(cursor, modelo)
        if colecao == -1:
            lead = 0
        else:
            try:
                lc = lotes.models.LeadColecao.objects.get(colecao=colecao)
                lead = lc.lead
            except models.LeadColecao.DoesNotExist:
                lead = 0

        if lead == 0:
            periodo = ''
        else:
            periodo = lead + 7

        data_ped = lotes.models.busca_pedido(
            cursor, modelo=modelo, periodo=':{}'.format(periodo))

        if len(data_ped) == 0:
            total_ped = 0
        else:
            totalize_data(data_ped, {
                'sum': ['QTD'],
                'count': [],
                'descr': {'REF': 'T:'}})
            total_ped = data_ped[-1]['QTD']

    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar Pedido',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'total_ped': total_ped,
    })
    return JsonResponse(data, safe=False)


def get_celula(grd, tam, cor):
    result = 0
    for linha in grd['data'][:-1]:
        if linha['cor'] == cor:
            if tam in linha:
                result = linha[tam]
            else:
                result = 0
            break
    return result


def soma_grades(g1, g2):
    return opera_grades(g1, g2, '+')


def subtrai_grades(g1, g2):
    return opera_grades(g1, g2, '-')


def opera_grades(g1, g2, operacao):
    tamanhos1 = set(g1['headers'][1:-1])
    tamanhos2 = set(g2['headers'][1:-1])
    tamanhos = list(tamanhos1.union(tamanhos2))
    s_tamanhos = produto.models.S_Tamanho.objects.all().values()
    tamanhos = sorted(
        tamanhos,
        key=lambda tam: [
            s_tam['ordem_tamanho']
            for s_tam in s_tamanhos
            if s_tam['tamanho_ref'] == tam
        ])

    cores1 = set([
        linha['cor']
        for linha in g1['data'][:-1]
    ])
    cores2 = set([
        linha['cor']
        for linha in g2['data'][:-1]
    ])
    cores = list(cores1.union(cores2))
    cores = sorted(cores)

    grade = {}
    grade['fields'] = ['cor', *tamanhos, 'total']
    grade['headers'] = ['Cor/Tamanho', *tamanhos, 'Total']
    grade['style'] = {
        i+2: 'text-align: right;'
        for i, _ in enumerate(tamanhos)
    }
    grade['style'][len(tamanhos)+2] = 'text-align: right; font-weight: bold;'
    grade['data'] = []
    linha_zerada = {
        tam: 0
        for tam in tamanhos
    }
    linha_zerada.update({
        'total': 0,
    })
    totais = linha_zerada.copy()

    for cor in cores:
        linha = linha_zerada.copy()
        linha['cor'] = cor
        total_linha = 0
        for tam in tamanhos:
            valor1 = get_celula(g1, tam, cor)
            valor2 = get_celula(g2, tam, cor)
            if operacao == '+':
                valor = valor1 + valor2
            else:
                valor = valor1 - valor2
            linha[tam] = valor
            totais[tam] += valor
            total_linha += valor
        linha['total'] = total_linha
        totais['total'] += total_linha
        grade['data'].append(linha)

    totais['cor'] = 'Total'
    totais['|STYLE'] = 'font-weight: bold;'
    grade['data'].append(totais)
    return grade


class GradeProduzir(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradeProduzir, self).__init__(*args, **kwargs)
        self.Form_class = comercial.forms.AnaliseModeloForm
        self.template_name = 'lotes/grade_produzir.html'
        self.title_name = 'Grade de modelo a produzir'
        self.get_args = ['modelo']

    def mount_context(self):
        cursor = connections['so'].cursor()

        modelo = self.form.cleaned_data['modelo']
        self.context.update({
            'modelo': modelo,
        })

        metas = comercial.models.MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            comercial.models.MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False, modelo=modelo)
        metas = metas.order_by('-meta_estoque')
        if len(metas) == 0:
            self.context.update({
                'msg_meta_estoque': 'Modelo sem meta de estoque definida',
                'msg_meta_giro': 'Modelo sem meta de giro definida',
            })
            return
        else:
            meta = metas[0]

        calcula_grade = False
        if meta.meta_estoque == 0:
            self.context.update({
                'msg_meta_estoque': 'Modelo com meta de estoque zerada',
            })
        else:
            gme = grade_meta_estoque(meta)
            self.context.update({
                'gme': gme,
            })
            calcula_grade = True

        if meta.meta_giro == 0:
            self.context.update({
                'msg_meta_giro': 'Modelo com meta de giro zerada',
            })
        else:
            colecao = produto.queries.colecao_de_modelo(
                cursor, meta.modelo)
            if colecao == -1:
                lead = 0
            else:
                try:
                    lc = lotes.models.LeadColecao.objects.get(
                        colecao=colecao)
                    lead = lc.lead
                except lotes.models.LeadColecao.DoesNotExist:
                    lead = 0

            gmg = grade_meta_giro(meta, lead, show_distrib=False)
            self.context.update({
                'gmg': gmg,
            })
            calcula_grade = True

        if not calcula_grade:
            return

        if meta.meta_estoque == 0:
            gm = gmg
        elif meta.meta_giro == 0:
            gm = gme
        else:
            gm = soma_grades(gme, gmg)

        self.context.update({
            'gm': gm,
        })

        g_header, g_fields, g_data, g_style, total = \
            lotes.models.op_sortimentos(
                cursor, tipo='a', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        if total != 0:
            self.context.update({
                'gop': {
                    'headers': g_header,
                    'fields': g_fields,
                    'data': g_data,
                    'style': g_style,
                }
            })

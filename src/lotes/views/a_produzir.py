from pprint import pprint
import copy

from django.db import connections
from django.db.models import Exists, OuterRef
from django.http import JsonResponse

from utils.views import totalize_data
from base.forms.forms2 import ModeloForm2
from base.views import O2BaseGetView, O2BaseGetPostView
from geral.functions import config_get_value

import comercial.models
from comercial.views.estoque import grade_meta_estoque
import produto.queries
import produto.models
import systextil.models
import estoque.queries

import lotes.models
import lotes.queries.op
import lotes.queries.pedido
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
            data_row['total_est'] = 0
            data_row['total_est|CLASS'] = 'total_est-{}'.format(row['modelo'])
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
            'sum': ['meta_giro', 'meta_estoque', 'meta',
                    'total_op', 'total_est', 'total_ped',
                    'op_menos_ped', 'a_produzir', 'excesso'],
            'count': [],
            'descr': {'modelo': 'Totais:'},
            'row_style': 'font-weight: bold;',
            'class_suffix': '__total',
        })

        dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
        self.context.update({
            'dias_alem_lead': dias_alem_lead,
            'headers': ['Modelo', 'Meta de estoque', 'Meta de giro (lead)',
                        'Total das metas(A)', 'Total das OPs',
                        'Total nos depósitos', 'Carteira de pedidos',
                        'OPs+Depósitos–Pedidos(B)', 'A produzir(A-B)[+]',
                        'Excesso(A-B)[-]'],
            'fields': ['modelo', 'meta_estoque', 'meta_giro',
                       'meta', 'total_op',
                       'total_est', 'total_ped',
                       'op_menos_ped', 'a_produzir',
                       'excesso'],
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
                10: 'text-align: right;',
            },
        })


def estoque_depositos_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        _, _, _, _, total_est = \
            estoque.queries.grade_estoque(
                cursor, dep=('101', '102', '231'), modelo=modelo)

    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao buscar estoque nos depósitos',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'total_est': total_est,
    })
    return JsonResponse(data, safe=False)


def op_producao_modelo(request, modelo):
    cursor = connections['so'].cursor()
    data = {
        'modelo': modelo,
    }

    try:
        data_op = lotes.queries.op.busca_op(
            cursor, modelo=modelo, tipo='v', tipo_alt='p',
            situacao='a', posicao='p', cached=True)

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
    dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)

    try:
        lead = produto.queries.lead_de_modelo(cursor, modelo)

        if lead == 0:
            periodo = ''
        else:
            periodo = lead + dias_alem_lead

        data_ped = lotes.queries.pedido.pedido_faturavel_modelo(
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
    sortimento_field = grd['fields'][0]
    for linha in grd['data'][:-1]:
        if linha[sortimento_field] == cor:
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


def zera_grade(g1):
    return opera_grades(g1, g1, '-')


def inverte_sinal_grade(g1):
    return opera_grade(g1, lambda x: -x)


def opera_grades(g1, g2, operacao):
    tamanhos1 = set(g1['headers'][1:-1])
    tamanhos2 = set(g2['headers'][1:-1])
    tamanhos = list(tamanhos1.union(tamanhos2))
    s_tamanhos = systextil.models.Tamanho.objects.all().values()
    tamanhos = sorted(
        tamanhos,
        key=lambda tam: [
            s_tam['ordem_tamanho']
            for s_tam in s_tamanhos
            if s_tam['tamanho_ref'] == tam
        ])

    sortimento_field1 = g1['fields'][0]
    sortimento_field2 = g2['fields'][0]
    cores1 = set([
        linha[sortimento_field1]
        for linha in g1['data'][:-1]
    ])
    cores2 = set([
        linha[sortimento_field2]
        for linha in g2['data'][:-1]
    ])
    cores = list(cores1.union(cores2))
    cores = sorted(cores)

    grade = {}
    grade['fields'] = [sortimento_field1, *tamanhos, 'total']
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
        linha[sortimento_field1] = cor
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

    totais[sortimento_field1] = 'Total'
    totais['|STYLE'] = 'font-weight: bold;'
    grade['data'].append(totais)
    return grade


def grade_filtra_linhas_zeradas(grd):
    grade = copy.deepcopy(grd)
    for linha in grade['data'][:-1]:
        if linha['Total'] == 0:
            grade['data'].remove(linha)
    return grade


def opera_grade(grd, func):
    grade = copy.deepcopy(grd)
    lin_tot = grade['data'][-1]
    col_tot = grade['fields'][-1]
    for linha in grade['data'][:-1]:
        for col in grade['fields'][1:-1]:
            ori = linha[col]
            linha[col] = func(linha[col])
            lin_tot[col] += (linha[col] - ori)
            linha[col_tot] += (linha[col] - ori)
            lin_tot[col_tot] += (linha[col] - ori)
    return grade


def update_gzerada(gzerada, gme):
    gzerada_aux = zera_grade(gme)
    if gzerada is None:
        return gzerada_aux
    else:
        return soma_grades(gzerada, gzerada_aux)


class GradeProduzirOld(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradeProduzirOld, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm2
        self.template_name = 'lotes/grade_produzir.html'
        self.title_name = 'Grade de modelo a produzir'
        self.get_args = ['modelo']

    def mount_context(self):
        cursor = connections['so'].cursor()

        modelo = self.form.cleaned_data['modelo']
        self.context.update({
            'modelo': modelo,
        })

        data = produto.queries.modelo_inform(cursor, modelo)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Modelo não encontrado',
            })
            return

        row = data[0]
        colecao = row['CODIGO_COLECAO']
        self.context.update({
            'colecao': row['COLECAO'],
            'descr': row['DESCR'],
        })

        lm_tam = 0
        lm_cor = 0
        try:
            LC = lotes.models.LeadColecao.objects.get(colecao=colecao)
            lm_tam = LC.lm_tam
            lm_cor = LC.lm_cor
        except lotes.models.LeadColecao.DoesNotExist:
            pass

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

        gzerada = None

        calcula_grade = False
        gme = None
        if meta.meta_estoque == 0:
            self.context.update({
                'msg_meta_estoque': 'Modelo com meta de estoque zerada',
            })
        else:
            gme = grade_meta_estoque(meta)
            calcula_grade = True
            gzerada = update_gzerada(gzerada, gme)

        lead = produto.queries.lead_de_modelo(cursor, modelo)
        gmg = None
        if meta.meta_giro == 0:
            self.context.update({
                'msg_meta_giro': 'Modelo com meta de giro zerada',
            })
        else:
            gmg = grade_meta_giro(meta, lead, show_distrib=False)
            calcula_grade = True
            gzerada = update_gzerada(gzerada, gmg)

        if not calcula_grade:
            return

        g_header, g_fields, g_data, g_style, total_opa = \
            lotes.queries.op.op_sortimentos(
                cursor, tipo='a', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        gopa = None
        if total_opa != 0:
            gopa = {
                'headers': g_header,
                'fields': g_fields,
                'data': g_data,
                'style': g_style,
            }
            gzerada = update_gzerada(gzerada, gopa)

        gf_header, gf_fields, gf_data, gf_style, total_opf = \
            lotes.queries.op.op_sortimentos(
                cursor, tipo='fpnf', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        gopf = None
        if total_opf != 0:
            gopf = {
                'headers': gf_header,
                'fields': gf_fields,
                'data': gf_data,
                'style': gf_style,
            }
            gopf = grade_filtra_linhas_zeradas(gopf)
            gzerada = update_gzerada(gzerada, gopf)

        gpf_header, gpf_fields, gpf_data, gpf_style, total_oppf = \
            lotes.queries.op.op_sortimentos(
                cursor, tipo='apf', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        goppf = None
        if total_oppf != 0:
            goppf = {
                'headers': gpf_header,
                'fields': gpf_fields,
                'data': gpf_data,
                'style': gpf_style,
            }
            goppf = inverte_sinal_grade(goppf)
            total_oppf = -total_oppf
            goppf = grade_filtra_linhas_zeradas(goppf)
            gzerada = update_gzerada(gzerada, goppf)

        dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
        self.context.update({
            'dias_alem_lead': dias_alem_lead,
        })

        if lead == 0:
            periodo = ''
        else:
            periodo = lead + dias_alem_lead

        gp_header, gp_fields, gp_data, gp_style, total_ped = \
            lotes.queries.pedido.sortimento(
                cursor, tipo_sort='c', descr_sort=False, modelo=modelo,
                cancelado='n', faturavel='f', total='Total',
                periodo=':{}'.format(periodo))

        gped = None
        if total_ped != 0:
            gped = {
                'headers': gp_header,
                'fields': gp_fields,
                'data': gp_data,
                'style': gp_style,
            }
            gzerada = update_gzerada(gzerada, gped)

        # Utiliza grade zerada para igualar cores e tamanhos das grades base
        # dos cálculos
        if gme is not None:
            gme = soma_grades(gzerada, gme)
            self.context.update({
                'gme': gme,
            })

        if gmg is not None:
            gmg = soma_grades(gzerada, gmg)
            self.context.update({
                'gmg': gmg,
            })

        if gopa is not None:
            gopa = soma_grades(gzerada, gopa)
            self.context.update({
                'gopa': gopa,
            })

        if gopf is not None:
            gopf = soma_grades(gzerada, gopf)
            self.context.update({
                'gopf': gopf,
            })

        if goppf is not None:
            goppf = soma_grades(gzerada, goppf)
            self.context.update({
                'goppf': goppf,
            })

        if gped is not None:
            gped = soma_grades(gzerada, gped)
            self.context.update({
                'gped': gped,
            })

        gop = None
        total_op = 0
        conta_grade_op = 0
        if gopf is None:
            if gopa is not None:
                conta_grade_op = 1
                gop = gopa
                total_op = total_opa
        else:
            if gopa is None:
                conta_grade_op = 1
                gop = gopf
                total_op = total_opf
            else:
                conta_grade_op = 2
                gop = soma_grades(gopa, gopf)
                total_op = total_opa + total_opf

        if goppf is not None:
            conta_grade_op += 1
            if gop is None:
                gop = goppf
            else:
                gop = soma_grades(gop, goppf)
            total_op += total_oppf

        self.context.update({
            'gop': gop,
            'conta_grade_op': conta_grade_op,
        })

        gm = None
        if meta.meta_estoque != 0 or meta.meta_giro != 0:
            if meta.meta_estoque == 0:
                gm = gmg
            elif meta.meta_giro == 0:
                gm = gme
            else:
                gm = soma_grades(gme, gmg)

            self.context.update({
                'gm': gm,
            })

        gopp = None
        if total_op != 0 or total_ped != 0:
            if total_ped == 0:
                gopp = gop
            elif total_op == 0:
                gopp = subtrai_grades(gzerada, gped)
            else:
                gopp = subtrai_grades(gop, gped)

            self.context.update({
                'gopp': gopp,
            })

        gresult = None
        if gopp is not None or gm is not None:
            if gopp is None:
                gresult = gm
            elif gm is None:
                gresult = gopp
            else:
                gresult = subtrai_grades(gm, gopp)

        glm = None
        glc = None

        if gresult is not None:
            gap = opera_grade(gresult, lambda x: x if x > 0 else 0)
            self.context.update({
                'gap': gap,
            })
            gex = opera_grade(gresult, lambda x: -x if x < 0 else 0)
            self.context.update({
                'gex': gex,
            })

            if lm_tam != 0 or lm_cor != 0:
                glm = copy.deepcopy(gap)

        if glm is not None:

            row_tot = glm['data'][-1]
            tam_conf = {}
            for row_cor in glm['data'][:-1]:
                field_tot = glm['fields'][-1]
                for tam in glm['fields'][1:-1]:
                    if tam not in tam_conf:
                        tam_conf[tam] = {
                            'min_para_lm': 0,
                            'lm_cor_sozinha': 's',
                        }
                        try:
                            RLM = lotes.models.RegraLMTamanho.objects.get(
                                tamanho=tam)
                            tam_conf[tam] = {
                                'min_para_lm': RLM.min_para_lm,
                                'lm_cor_sozinha': RLM.lm_cor_sozinha,
                            }
                        except lotes.models.RegraLMTamanho.DoesNotExist:
                            pass

                    if lm_tam != 0 and row_cor[tam] != 0:
                        lm_lim = round(
                            lm_tam * tam_conf[tam]['min_para_lm'] / 100, 0)
                        if row_cor[tam] < lm_tam:
                            if row_cor[tam] >= lm_lim:
                                row_tot[field_tot] += lm_tam - row_cor[tam]
                                row_tot[tam] += lm_tam - row_cor[tam]
                                row_cor[field_tot] += lm_tam - row_cor[tam]
                                row_cor[tam] = lm_tam
                            else:
                                row_tot[field_tot] += -row_cor[tam]
                                row_tot[tam] += -row_cor[tam]
                                row_cor[field_tot] += -row_cor[tam]
                                row_cor[tam] = 0
                            row_cor['{}|STYLE'.format(tam)] = \
                                'font-weight: bold; color: red'

            if glm != gap:
                self.context.update({
                    'glm': glm,
                })

            glc = copy.deepcopy(glm)

        if glc is not None:
            row_tot = glc['data'][-1]
            for row_cor in glc['data'][:-1]:
                tam_count = 0
                tam_tot = 0
                field_tot = glc['fields'][-1]
                for tam in glc['fields'][1:-1]:
                    if row_cor[tam] != 0:
                        tam_count += 1
                    tam_tot += row_cor[tam]

                lm_cor_acresc = 0
                if tam_tot != 0 and lm_cor != 0:
                    if tam_tot < lm_cor:
                        if tam_count > 1 or \
                                tam_conf[tam]['lm_cor_sozinha'] == 's':
                            lm_cor_acresc = lm_cor - tam_tot
                if lm_cor_acresc > 0:
                    tam_tot_final = 0
                    tam_ult = None
                    for tam in glc['fields'][1:-1]:
                        if row_cor[tam] > 0:
                            tam_ult = tam
                            acrescenta = round(
                                lm_cor_acresc / tam_tot * row_cor[tam],
                                0)
                            row_tot[field_tot] += acrescenta
                            row_tot[tam] += acrescenta
                            row_cor[field_tot] += acrescenta
                            row_cor[tam] += acrescenta
                            row_cor['{}|STYLE'.format(tam)] = \
                                'font-weight: bold; color: red'
                            tam_tot_final += row_cor[tam]

                    # em caso de distribuição do lm_cor por mais de uma cor
                    # o arredondamento pode não formar lm_cor. Se total ainda
                    # estiver abaico do lm_cor, acrescentar ao último tamanho
                    # alterado
                    lm_cor_acresc = lm_cor - tam_tot_final
                    if lm_cor_acresc > 0:
                        if tam_ult is not None:
                            row_tot[field_tot] += lm_cor_acresc
                            row_tot[tam] += lm_cor_acresc
                            row_cor[field_tot] += lm_cor_acresc
                            row_cor[tam] += lm_cor_acresc

            if glc != glm:
                self.context.update({
                    'glc': glc,
                })

import copy
import sys
from pprint import pprint

from django.db.models import Exists, OuterRef

from fo2.connections import db_cursor_so

from base.forms.forms2 import ModeloForm2
from base.views import O2BaseGetPostView
from geral.functions import config_get_value
from utils.functions.dictlist.dictlist_to_grade import dictlist_to_grade_qtd
from utils.functions.dictlist.operacoes_grade import OperacoesGrade
from utils.views import totalize_data

import comercial.models
import produto.models
import produto.queries
from cd.queries.novo_modulo import refs_em_palets
from comercial.models.functions.meta_referencia import meta_ref_incluir
from comercial.views.estoque import grade_meta_estoque

import lotes.models
import lotes.queries.op
import lotes.queries.pedido
from lotes.views.parametros_functions import grade_meta_giro


class ProduzirGradeEmpenho(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(ProduzirGradeEmpenho, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm2
        self.template_name = 'lotes/analise/produzir_grade_empenho.html'
        self.title_name = 'A produzir, por grade, empenho e carteira'
        self.get_args = ['modelo']

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        og = OperacoesGrade()

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
            LC = lotes.models.RegraColecao.objects.get(colecao=colecao)
            lm_tam = LC.lm_tam
            lm_cor = LC.lm_cor
        except lotes.models.RegraColecao.DoesNotExist:
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
            gzerada = og.update_gzerada(gzerada, gme)

        lead = produto.queries.lead_de_modelo(cursor, modelo)
        gmg = None
        if meta.meta_giro == 0:
            self.context.update({
                'msg_meta_giro': 'Modelo com meta de giro zerada',
            })
        else:
            gmg = grade_meta_giro(meta, lead, show_distrib=False)
            calcula_grade = True
            gzerada = og.update_gzerada(gzerada, gmg)

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
            gzerada = og.update_gzerada(gzerada, gopa)

        empenhado = refs_em_palets.query(
            cursor,
            fields='all',
            modelo=modelo,
            selecao_lotes='qq',
            paletizado='s',
        )

        grade_inventario = dictlist_to_grade_qtd(
            empenhado,
            field_linha='cor',
            field_coluna='tam',
            facade_coluna='Tamanho',
            field_ordem_coluna='ordem_tam',
            field_quantidade='qtd',
        )
        total_inv = grade_inventario['total']

        ginv = None
        if total_inv != 0:
            ginv = {
                'headers': grade_inventario['headers'],
                'fields': grade_inventario['fields'],
                'data': grade_inventario['data'],
                'style': grade_inventario['style'],
            }
            gzerada = og.update_gzerada(gzerada, ginv)

        for row in empenhado:
            row['qtd'] = row['qtd_emp'] + row['qtd_sol']

        grade_empenhado = dictlist_to_grade_qtd(
            empenhado,
            field_linha='cor',
            field_coluna='tam',
            facade_coluna='Tamanho',
            field_ordem_coluna='ordem_tam',
            field_quantidade='qtd',
        )
        total_sol = grade_empenhado['total']

        gsol = None
        if total_sol != 0:
            gsol = {
                'headers': grade_empenhado['headers'],
                'fields': grade_empenhado['fields'],
                'data': grade_empenhado['data'],
                'style': grade_empenhado['style'],
            }
            gzerada = og.update_gzerada(gzerada, gsol)

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
                cancelado='n', faturavel='f', total='Total', solicitado='n',
                pedido_liberado='s',
                periodo=':{}'.format(periodo))

        gped = None
        if total_ped != 0:
            gped = {
                'headers': gp_header,
                'fields': gp_fields,
                'data': gp_data,
                'style': gp_style,
            }
            gzerada = og.update_gzerada(gzerada, gped)

        refs_adicionadas = meta_ref_incluir(cursor, modelo)
        # pprint(gped)
        # pprint(refs_adicionadas)

        for row_ref in refs_adicionadas:
            # print(row_ref['referencia'])
            gadd = None
            if row_ref['ok']:

                ga_header, ga_fields, ga_data, ga_style, total_add = \
                    lotes.queries.pedido.sortimento(
                        cursor, tipo_sort='c', descr_sort=False, ref=row_ref['referencia'],
                        cancelado='n', faturavel='f', total='Total', solicitado='n',
                        pedido_liberado='s',
                        periodo=':{}'.format(periodo))

                if total_add != 0:
                    gadd = {
                        'headers': ga_header,
                        'fields': ga_fields,
                        'data': ga_data,
                        'style': ga_style,
                    }

            if gadd:
                # pprint(gadd)
                gpac = copy.deepcopy(gzerada)
                # pprint(gpac)
                gadd_sortimento_field = gadd['fields'][0]
                gadd_total_field = gadd['fields'][-1]
                gpac_sortimento_field = gpac['fields'][0]
                for ga_row in gadd['data']:
                    if (
                        ga_row[gadd_total_field] > 0 and
                        ga_row[gadd_sortimento_field] != 'Total'
                    ):
                        cor0 = ga_row[gadd_sortimento_field].lstrip("0")
                        ga_row_quants = {
                            key: ga_row[key]
                            for key in ga_row
                            if key not in (gadd_sortimento_field, gadd_total_field)
                        }
                        ga_row_comb = row_ref['cores_dict'][cor0]
                        for ga_row_comb_cor0 in ga_row_comb:
                            ga_row_comb_cor = ga_row_comb_cor0.zfill(6)
                            gpac_row = [
                                row
                                for row in gpac['data']
                                if row[gpac_sortimento_field] == ga_row_comb_cor
                            ][0]
                            for ga_row_comb_tam in ga_row_quants:
                                gpac_row[ga_row_comb_tam] += (
                                    ga_row_quants[ga_row_comb_tam] *
                                    ga_row_comb[ga_row_comb_cor0]
                                )
                # pprint(gpac)
                gped = og.soma_grades(gped, gpac)
                # pprint(gped)

        # Utiliza grade zerada para igualar cores e tamanhos das grades base
        # dos cálculos
        if gme is not None:
            gme = og.soma_grades(gzerada, gme)
            self.context.update({
                'gme': gme,
            })

        if gmg is not None:
            gmg = og.soma_grades(gzerada, gmg)
            self.context.update({
                'gmg': gmg,
            })

        if gopa is not None:
            gopa = og.soma_grades(gzerada, gopa)
            self.context.update({
                'gopa': gopa,
            })

        if ginv is not None:
            ginv = og.soma_grades(gzerada, ginv)
            self.context.update({
                'ginv': ginv,
            })

        if gsol is not None:
            gsol = og.soma_grades(gzerada, gsol)
            self.context.update({
                'gsol': gsol,
            })

        if gped is not None:
            gped = og.soma_grades(gzerada, gped)
            self.context.update({
                'gped': gped,
            })

        gm = None
        if meta.meta_estoque != 0 or meta.meta_giro != 0:
            if meta.meta_estoque == 0:
                gm = gmg
            elif meta.meta_giro == 0:
                gm = gme
            else:
                gm = og.soma_grades(gme, gmg)

            self.context.update({
                'gm': gm,
            })
        
        gopa_ncd = None
        if total_inv != 0 and total_opa != total_inv:
            gopa_ncd = og.subtrai_grades(gopa, ginv)
            self.context.update({
                'gopa_ncd': gopa_ncd,
            })

        gopp1 = None
        if total_opa != 0 or total_ped != 0:
            if total_ped == 0:
                gopp1 = gopa
            elif total_opa == 0:
                gopp1 = og.subtrai_grades(gzerada, gped)
            else:
                gopp1 = og.subtrai_grades(gopa, gped)

        gopp2 = None
        if gopp1 or total_sol != 0:
            if total_sol == 0:
                gopp2 = gopp1
            elif gopp1 is None:
                gopp2 = og.subtrai_grades(gzerada, gsol)
            else:
                gopp2 = og.subtrai_grades(gopp1, gsol)

        gopp = None
        if gopp2:
            gopp = gopp2
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
                gresult = og.subtrai_grades(gm, gopp)

        glm = None
        glc = None

        if gresult is not None:
            gap = og.opera_grade(gresult, lambda x: x if x > 0 else 0)
            self.context.update({
                'gap': gap,
            })
            gex = og.opera_grade(gresult, lambda x: -x if x < 0 else 0)
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

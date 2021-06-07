from pprint import pprint

from django.conf import settings
from django.db.models import Exists, OuterRef
from django.urls import reverse

from fo2.connections import db_cursor_so

from base.forms.forms2 import ModeloForm2
from base.views import O2BaseGetPostView

import comercial
import produto
import lotes
import estoque
from comercial.models.functions.meta_referencia import meta_ref_incluir
from comercial.views.estoque import grade_meta_estoque

from lotes.views.a_produzir import *


class GradeProduzir(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradeProduzir, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm2
        self.template_name = 'lotes/analise/grade_produzir.html'
        self.title_name = 'A produzir, por grade, depósito'
        self.get_args = ['modelo']

    def adiciona_referencia_em_modelo(self, ref_adicionada, r_gpr_fields, r_gpr_data, gpr_data):
        for index, row in enumerate(r_gpr_data):
            ref_cor = row['SORTIMENTO'].lstrip("0")
            if ref_cor in ref_adicionada['cores_dict']:
                combinacao = ref_adicionada['cores_dict'][ref_cor]
                for cor in combinacao:
                    try:
                        av_row = next(
                            item
                            for item in gpr_data
                            if item["SORTIMENTO"].lstrip("0") == cor
                        )
                    except StopIteration:
                        gpr_data.insert(index, row.copy())
                        av_row = gpr_data[index]
                        for tamanho in r_gpr_fields[1:-1]:
                            av_row[tamanho] = 0
                    for tamanho in r_gpr_fields[1:-1]:
                        if tamanho in row:
                            try:
                                av_row[tamanho] += row[tamanho] * combinacao[cor]
                            except KeyError:
                                av_row[tamanho] = row[tamanho] * combinacao[cor]

    def mount_context(self):
        cursor = db_cursor_so(self.request)

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

        if settings.DEBUG:
            refs_adicionadas = meta_ref_incluir(cursor, modelo)
        else:
            refs_adicionadas = []
        self.context.update({
            'adicionadas': refs_adicionadas,
        })

        gpr_header, gpr_fields, gpr_data, gpr_style, total_oppr = \
            lotes.queries.op.op_sortimentos(
                cursor, tipo='ap', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        for ref_adicionada in refs_adicionadas:
            if ref_adicionada['ok']:
                _, r_gpr_fields, r_gpr_data, _, r_total_oppr = \
                    lotes.queries.op.op_sortimentos(
                        cursor, tipo='ap', descr_sort=False, referencia=ref_adicionada['referencia'],
                        situacao='a', tipo_ref='v', tipo_alt='p', total='Total')
                if r_total_oppr != 0:
                    total_oppr += r_total_oppr * ref_adicionada['conta_componentes']
                    self.adiciona_referencia_em_modelo(ref_adicionada, r_gpr_fields, r_gpr_data, gpr_data)

        goppr = None
        if total_oppr != 0:
            goppr = {
                'headers': gpr_header,
                'fields': gpr_fields,
                'data': gpr_data,
                'style': gpr_style,
            }
            gzerada = update_gzerada(gzerada, goppr)

        gcd_header, gcd_fields, gcd_data, gcd_style, total_opcd = \
            lotes.queries.op.op_sortimentos(
                cursor, tipo='acd', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        for ref_adicionada in refs_adicionadas:
            if ref_adicionada['ok']:
                _, r_gcd_fields, r_gcd_data, _, r_total_opcd = \
                    lotes.queries.op.op_sortimentos(
                        cursor, tipo='acd', descr_sort=False, referencia=ref_adicionada['referencia'],
                        situacao='a', tipo_ref='v', tipo_alt='p', total='Total')
                if r_total_opcd != 0:
                    total_opcd += r_total_opcd * ref_adicionada['conta_componentes']
                    self.adiciona_referencia_em_modelo(ref_adicionada, r_gcd_fields, r_gcd_data, gcd_data)

        gopcd = None
        if total_opcd != 0:
            gopcd = {
                'headers': gcd_header,
                'fields': gcd_fields,
                'data': gcd_data,
                'style': gcd_style,
            }
            gzerada = update_gzerada(gzerada, gopcd)

        e_header, e_fields, e_data, e_style, total_est = \
            estoque.queries.grade_estoque(
                cursor, dep=('101', '102', '231'), modelo=modelo)

        for ref_adicionada in refs_adicionadas:
            if ref_adicionada['ok'] and 1==1:
                _, r_e_fields, r_e_data, _, r_total_est = \
                    estoque.queries.grade_estoque(
                        cursor, dep=('101', '102', '231'), referencia=ref_adicionada['referencia'])
                if r_total_est != 0:
                    total_est += r_total_est * ref_adicionada['conta_componentes']
                    self.adiciona_referencia_em_modelo(ref_adicionada, r_e_fields, r_e_data, e_data)

        gest = None
        if total_est != 0:
            gest = {
                'headers': e_header,
                'fields': e_fields,
                'data': e_data,
                'style': e_style,
            }
            gzerada = update_gzerada(gzerada, gest)

        dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
        self.context.update({
            'dias_alem_lead': dias_alem_lead,
        })

        if lead == 0:
            periodo = ''
        else:
            periodo = lead + dias_alem_lead

        gp_header, gp_fields, gp_data, gp_style, total_ped = \
            lotes.queries.pedido.pedido_faturavel_modelo_sortimento(
                cursor, modelo=modelo,
                periodo=':{}'.format(periodo), cached=False
            )

        for ref_adicionada in refs_adicionadas:
            if ref_adicionada['ok'] and 1==1:
                _, r_gp_fields, r_gp_data, _, r_total_ped = \
                    lotes.queries.pedido.pedido_faturavel_modelo_sortimento(
                        cursor, referencia=ref_adicionada['referencia'],
                        periodo=':{}'.format(periodo), cached=False
                    )
                if r_total_ped != 0:
                    total_ped += r_total_ped * ref_adicionada['conta_componentes']
                    self.adiciona_referencia_em_modelo(ref_adicionada, r_gp_fields, r_gp_data, gp_data)

        gped = None
        if total_ped != 0:
            self.context.update({
                'gped_header_link': reverse(
                    'producao:pedido_faturavel_modelo__get', args=[modelo]),
            })
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

        if goppr is not None:
            goppr = soma_grades(gzerada, goppr)
            self.context.update({
                'goppr': goppr,
            })

        if gopcd is not None:
            gopcd = soma_grades(gzerada, gopcd)
            self.context.update({
                'gopcd': gopcd,
            })

        if gest is not None:
            gest = soma_grades(gzerada, gest)
            self.context.update({
                'gest': gest,
            })

        if gped is not None:
            gped = soma_grades(gzerada, gped)
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
                gm = soma_grades(gme, gmg)

            self.context.update({
                'gm': gm,
            })

        if total_opcd != 0 and total_oppr == 0:
            gop = gopcd
            total_op = total_opcd
        elif total_opcd == 0 and total_oppr != 0:
            gop = goppr
            total_op = total_oppr
        elif total_opcd != 0 and total_oppr != 0:
            gop = soma_grades(goppr, gopcd)
            total_op = total_oppr + total_opcd
        else:
            gop = None
            total_op = 0
        if gop is not None:
            self.context.update({
                'gop': gop,
            })

        gopp = None
        if total_op != 0 or total_est != 0 or total_ped != 0:
            if total_ped == 0:
                if total_est == 0:
                    gopp = gop
                if total_op == 0:
                    gopp = gest
                else:
                    gopp = soma_grades(gop, gest)
            elif total_op == 0:
                if total_est == 0:
                    gopp = subtrai_grades(gzerada, gped)
                else:
                    gopp = subtrai_grades(gest, gped)
            else:
                if total_est == 0:
                    gopp = subtrai_grades(gop, gped)
                else:
                    gopp = soma_grades(gop, gest)
                    gopp = subtrai_grades(gopp, gped)

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
                            acrescenta = int(round(
                                lm_cor_acresc / tam_tot * row_cor[tam],
                                0))
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

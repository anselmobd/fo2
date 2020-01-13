from django.db import connections
from django.db.models import Exists, OuterRef

from base.views import O2BaseGetPostView

import comercial
import produto
import lotes
import estoque
from comercial.views.estoque import grade_meta_estoque
from lotes.views.a_produzir import *


class GradeProduzir(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradeProduzir, self).__init__(*args, **kwargs)
        self.Form_class = comercial.forms.AnaliseModeloForm
        self.template_name = 'lotes/analises/grade_produzir.html'
        self.title_name = 'Grade de modelo a produzir (estoque)'
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

        colecao = produto.queries.colecao_de_modelo(
            cursor, modelo)
        if colecao == -1:
            lead = 0
        else:
            try:
                lc = lotes.models.LeadColecao.objects.get(
                    colecao=colecao)
                lead = lc.lead
            except lotes.models.LeadColecao.DoesNotExist:
                lead = 0
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

        g_header, g_fields, g_data, g_style, total_op = \
            lotes.queries.op.op_sortimentos(
                cursor, tipo='a', descr_sort=False, modelo=modelo,
                situacao='a', tipo_ref='v', tipo_alt='p', total='Total')

        gop = None
        if total_op != 0:
            gop = {
                'headers': g_header,
                'fields': g_fields,
                'data': g_data,
                'style': g_style,
            }
            gzerada = update_gzerada(gzerada, gop)

        e_header, e_fields, e_data, e_style, total_est = \
            estoque.queries.grade_estoque(
                cursor, dep=('101', '102', '231'), modelo=modelo)
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

        # gp_header, gp_fields, gp_data, gp_style, total_ped = \
        #     lotes.queries.pedido.sortimento(
        #         cursor, tipo_sort='c', descr_sort=False, modelo=modelo,
        #         cancelado='n', faturavel='f', total='Total',
        #         periodo=':{}'.format(periodo))
        gp_header, gp_fields, gp_data, gp_style, total_ped = \
            lotes.queries.pedido.pedido_faturavel_modelo_sortimento(
                cursor, modelo=modelo, periodo=':{}'.format(periodo),
                cached=False
            )
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

        if gop is not None:
            gop = soma_grades(gzerada, gop)
            self.context.update({
                'gop': gop,
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

        gopp = None
        if total_op != 0 or total_est != 0 or total_ped != 0:
            if total_ped == 0:
                if total_est == 0:
                    gopp = gop
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

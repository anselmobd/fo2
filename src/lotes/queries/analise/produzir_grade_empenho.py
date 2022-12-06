import copy
from pprint import pprint

from django.core.cache import cache
from django.db.models import Exists, OuterRef

from geral.functions import config_get_value
from utils.cache import timeout
from utils.functions import (
    my_make_key_cache,
    loginfo,
)
from utils.functions.dictlist.dictlist_to_grade import dictlist_to_grade_qtd
from utils.functions.dictlist.operacoes_grade import OperacoesGrade

from cd.queries.novo_modulo import refs_em_palets
from comercial.models import MetaEstoque
from comercial.models.functions.meta_referencia import meta_ref_incluir
from comercial.views.estoque import grade_meta_estoque
from produto.queries import (
    lead_de_modelo,
    modelo_inform,
)

from lotes.models import (
    RegraColecao,
    RegraLMTamanho,
)
from lotes.queries.op.producao import op_producao
from lotes.queries.pedido import sortimento
from lotes.views.parametros_functions import grade_meta_giro

__all__ = ['MountProduzirGradeEmpenho']


class MountProduzirGradeEmpenho():

    def __init__(self, cursor, modelo):
        self.cursor = cursor
        self.modelo = modelo

    def cache_get(self):
        self.key_cache = my_make_key_cache(
            'lotes/queries/analise/produzir_grade_empenho/MPGE/query',
            self.modelo,
        )
        self.mount_produzir = cache.get(self.key_cache)
        if self.mount_produzir:
            loginfo('cached '+self.key_cache)
            return True

    def cache_set(self):
        cache.set(self.key_cache, self.mount_produzir, timeout=timeout.MINUTES_5)
        loginfo('calculated '+self.key_cache)

    def regra_colecao(self):
        lm_tam = 0
        lm_cor = 0
        try:
            LC = RegraColecao.objects.get(colecao=self.colecao)
            lm_tam = LC.lm_tam
            lm_cor = LC.lm_cor
        except RegraColecao.DoesNotExist:
            pass
        return lm_tam, lm_cor

    def get_meta_estoque(self):
        metas = MetaEstoque.objects
        metas = metas.annotate(antiga=Exists(
            MetaEstoque.objects.filter(
                modelo=OuterRef('modelo'),
                data__gt=OuterRef('data')
            )
        ))
        metas = metas.filter(antiga=False, modelo=self.modelo)
        metas = metas.order_by('-meta_estoque')
        return metas

    def get_gme(self):
        if self.meta.meta_estoque == 0:
            self.context.update({
                'msg_meta_estoque': 'Modelo com meta de estoque zerada',
            })
            return None
        g_m_e = grade_meta_estoque(self.meta)
        self.gzerada = self.og.update_gzerada(self.gzerada, g_m_e)
        return g_m_e

    def get_gmg(self):
        if self.meta.meta_giro == 0:
            self.context.update({
                'msg_meta_giro': 'Modelo com meta de giro zerada',
            })
            return None
        g_m_g = grade_meta_giro(self.meta, self.lead, show_distrib=False)
        self.gzerada = self.og.update_gzerada(self.gzerada, g_m_g)
        return g_m_g

    def op_nao_finalizada(self, modelo=None):
        data_op_p = op_producao(
            self.cursor, modelo=modelo,
            tipo_ref='v', tipo_op='p', tipo_selecao='a'
        )

        g_data_op_p = dictlist_to_grade_qtd(
            dados=data_op_p,
            field_linha='cor',
            new_field_linha='SORTIMENTO',
            facade_linha='Cores',
            field_coluna='tam',
            facade_coluna='Tamanhos',
            field_ordem_coluna='ordem_tam',
            field_quantidade='qtd',
        )

        qtds = None
        if g_data_op_p['total_abs']:
            qtds = {
                'headers': g_data_op_p['headers'],
                'fields': g_data_op_p['fields'],
                'data': g_data_op_p['data'],
                'style': g_data_op_p['style'],
            }
            self.gzerada = self.og.update_gzerada(self.gzerada, qtds)

        return qtds, g_data_op_p['total']

    def query(self):
        if self.cache_get():
            return self.mount_produzir

        self.og = OperacoesGrade()
        self.modelo = f"{self.modelo}"
        self.modelo = int(self.modelo)

        self.mount_produzir = {
            'modelo': self.modelo,
        }

        data_modelo = modelo_inform(self.cursor, self.modelo)
        if not data_modelo:
            self.mount_produzir.update({
                'msg_erro': 'Modelo não encontrado',
            })
            return self.mount_produzir

        row_modelo = data_modelo[0]
        self.colecao = row_modelo['CODIGO_COLECAO']
        self.mount_produzir.update({
            'colecao': row_modelo['COLECAO'],
            'descr': row_modelo['DESCR'],
        })

        lm_tam, lm_cor = self.regra_colecao()

        metas = self.get_meta_estoque()
        if not metas:
            self.mount_produzir.update({
                'msg_meta_estoque': 'Modelo sem meta de estoque definida',
                'msg_meta_giro': 'Modelo sem meta de giro definida',
            })
            return self.mount_produzir
        else:
            self.meta = metas[0]

        self.gzerada = None

        self.gme = self.get_gme()

        self.lead = lead_de_modelo(self.cursor, self.modelo)
        self.mount_produzir['lead'] = self.lead

        self.gmg = self.get_gmg()

        if not (self.gme or self.gmg):
            return self.mount_produzir

        gopa, total_opa = self.op_nao_finalizada(modelo=self.modelo)

        inventario = refs_em_palets.query(
            self.cursor,
            fields='all',
            modelo=self.modelo,
            selecao_lotes='63',
            paletizado='s',
        )
        grade_inventario = dictlist_to_grade_qtd(
            inventario,
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
            self.gzerada = self.og.update_gzerada(self.gzerada, ginv)

        empenhado = refs_em_palets.query(
            self.cursor,
            fields='all',
            modelo=self.modelo,
            selecao_lotes='qq',
            paletizado='t',
        )

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
            self.gzerada = self.og.update_gzerada(self.gzerada, gsol)

        dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
        self.mount_produzir.update({
            'dias_alem_lead': dias_alem_lead,
        })

        if self.lead == 0:
            periodo = ''
        else:
            periodo = self.lead + dias_alem_lead

        gp_header, gp_fields, gp_data, gp_style, total_ped = \
            sortimento(
                self.cursor, tipo_sort='c', descr_sort=False, modelo=self.modelo,
                cancelado='n', faturavel='f', total='Total', solicitado='n',
                agrupado='n', pedido_liberado='s',
                periodo=':{}'.format(periodo))

        gped = None
        if total_ped != 0:
            gped = {
                'headers': gp_header,
                'fields': gp_fields,
                'data': gp_data,
                'style': gp_style,
            }
            self.gzerada = self.og.update_gzerada(self.gzerada, gped)

        refs_adicionadas = meta_ref_incluir(self.cursor, self.modelo)

        for row_ref in refs_adicionadas:
            gadd = None
            if row_ref['ok']:

                ga_header, ga_fields, ga_data, ga_style, total_add = \
                    sortimento(
                        self.cursor, tipo_sort='c', descr_sort=False, ref=row_ref['referencia'],
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
                gpac = copy.deepcopy(self.gzerada)
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
                gped = self.og.soma_grades(gped, gpac)

        # Utiliza grade zerada para igualar cores e tamanhos das grades base
        # dos cálculos
        if self.gme is not None:
            self.gme = self.og.soma_grades(self.gzerada, self.gme)
            self.mount_produzir.update({
                'gme': self.gme,
            })

        if self.gmg is not None:
            self.gmg = self.og.soma_grades(self.gzerada, self.gmg)
            self.mount_produzir.update({
                'gmg': self.gmg,
            })

        if gopa is not None:
            gopa = self.og.soma_grades(self.gzerada, gopa)
            self.mount_produzir.update({
                'gopa': gopa,
            })

        if ginv is not None:
            ginv = self.og.soma_grades(self.gzerada, ginv)
            self.mount_produzir.update({
                'ginv': ginv,
            })

        if gsol is not None:
            gsol = self.og.soma_grades(self.gzerada, gsol)
            self.mount_produzir.update({
                'gsol': gsol,
            })

        if gped is not None:
            gped = self.og.soma_grades(self.gzerada, gped)
            self.mount_produzir.update({
                'gped': gped,
            })

        gm = None
        if self.meta.meta_estoque != 0 or self.meta.meta_giro != 0:
            if self.meta.meta_estoque == 0:
                gm = self.gmg
            elif self.meta.meta_giro == 0:
                gm = self.gme
            else:
                gm = self.og.soma_grades(self.gme, self.gmg)

            self.mount_produzir.update({
                'gm': gm,
            })
        
        gopa_ncd = None
        if total_inv != 0 and total_opa != total_inv:
            gopa_ncd = self.og.subtrai_grades(gopa, ginv)
            self.mount_produzir.update({
                'gopa_ncd': gopa_ncd,
            })

        gopp1 = None
        if total_opa != 0 or total_ped != 0:
            if total_ped == 0:
                gopp1 = gopa
            elif total_opa == 0:
                gopp1 = self.og.subtrai_grades(self.gzerada, gped)
            else:
                gopp1 = self.og.subtrai_grades(gopa, gped)

        gopp2 = None
        if gopp1 or total_sol != 0:
            if total_sol == 0:
                gopp2 = gopp1
            elif gopp1 is None:
                gopp2 = self.og.subtrai_grades(self.gzerada, gsol)
            else:
                gopp2 = self.og.subtrai_grades(gopp1, gsol)

        gopp = None
        if gopp2:
            gopp = gopp2
            self.mount_produzir.update({
                'gopp': gopp,
            })

        gresult = None
        if gopp is not None or gm is not None:
            if gopp is None:
                gresult = gm
            elif gm is None:
                gresult = gopp
            else:
                gresult = self.og.subtrai_grades(gm, gopp)

        glm = None
        glc = None

        if gresult is not None:
            gap = self.og.opera_grade(gresult, lambda x: x if x > 0 else 0)
            self.mount_produzir.update({
                'gap': gap,
            })
            gex = self.og.opera_grade(gresult, lambda x: -x if x < 0 else 0)
            self.mount_produzir.update({
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
                            RLM = RegraLMTamanho.objects.get(
                                tamanho=tam)
                            tam_conf[tam] = {
                                'min_para_lm': RLM.min_para_lm,
                                'lm_cor_sozinha': RLM.lm_cor_sozinha,
                            }
                        except RegraLMTamanho.DoesNotExist:
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
                self.mount_produzir.update({
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
                self.mount_produzir.update({
                    'glc': glc,
                })

        self.cache_set()

        return self.mount_produzir

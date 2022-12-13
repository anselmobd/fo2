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
from lotes.queries.pedido import (
    grade_pedido,
    sortimento,
)
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
        self.context = cache.get(self.key_cache)
        if self.context:
            loginfo('cached '+self.key_cache)
            return True

    def cache_set(self):
        cache.set(self.key_cache, self.context, timeout=timeout.MINUTES_5)
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

    def to_grade_e_total(self, dados=None):
        g_dados = dictlist_to_grade_qtd(
            dados=dados,
            field_linha='cor',
            field_coluna='tam',
            facade_coluna='Tamanho',
            field_ordem_coluna='ordem_tam',
            field_quantidade='qtd',
        )

        grade = None
        if g_dados['total_abs']:
            grade = {
                'headers': g_dados['headers'],
                'fields': g_dados['fields'],
                'data': g_dados['data'],
                'style': g_dados['style'],
            }
            self.gzerada = self.og.update_gzerada(self.gzerada, grade)

        return grade, g_dados['total']

    def get_em_producao(self):
        return op_producao(
            self.cursor,
            modelo=self.modelo,
            tipo_ref='v',
            tipo_op='p',
            tipo_selecao='a',
        )

    def get_inventario(self):
        return refs_em_palets.query(
            self.cursor,
            fields='all',
            modelo=self.modelo,
            selecao_lotes='63',
            paletizado='s',
        )

    def get_empenhado(self):
        empenhado = refs_em_palets.query(
            self.cursor,
            fields='all',
            modelo=self.modelo,
            selecao_lotes='qq',
            paletizado='t',
        )
        for row in empenhado:
            row['qtd'] = row['qtd_emp'] + row['qtd_sol']
        return empenhado

    def get_grade_pedido(self, ref=None, modelo=None):
        return grade_pedido.query(
            self.cursor,
            ref=ref,
            modelo=modelo,
            periodo=f':{self.periodo}',
            cancelado='n',
            liberado='s',
            faturavel='f',
            solicitado='n',
            agrupado_em_solicitacao='n',
        )

    def add_refs_pacote(self, gped, total_ped):
        refs_adicionadas = meta_ref_incluir(self.cursor, self.modelo)

        for row_ref in refs_adicionadas:
            gadd = None
            if row_ref['ok']:
                gadd, total_add = self.to_grade_e_total(
                    dados=self.get_grade_pedido(ref=row_ref['referencia'])
                )

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
                total_ped += total_add

        return gped, total_ped

    def cortam2context(self, nome, grade):
        if grade:
            grade = self.og.soma_grades(self.gzerada, grade)
            self.context.update({
                nome: grade,
            })

    def mount_context(self):
        if self.cache_get():
            return self.context

        self.og = OperacoesGrade()
        self.modelo = f"{self.modelo}"
        self.modelo = int(self.modelo)

        self.context = {
            'modelo': self.modelo,
        }

        data_modelo = modelo_inform(self.cursor, self.modelo)
        if not data_modelo:
            self.context.update({
                'msg_erro': 'Modelo não encontrado',
            })
            return self.context

        row_modelo = data_modelo[0]
        self.colecao = row_modelo['CODIGO_COLECAO']
        self.context.update({
            'colecao': row_modelo['COLECAO'],
            'descr': row_modelo['DESCR'],
        })

        lm_tam, lm_cor = self.regra_colecao()

        metas = self.get_meta_estoque()
        if not metas:
            self.context.update({
                'msg_meta_estoque': 'Modelo sem meta de estoque definida',
                'msg_meta_giro': 'Modelo sem meta de giro definida',
            })
            return self.context
        else:
            self.meta = metas[0]

        self.gzerada = None

        self.gme = self.get_gme()

        self.lead = lead_de_modelo(self.cursor, self.modelo)
        self.context['lead'] = self.lead

        self.gmg = self.get_gmg()

        if not (self.gme or self.gmg):
            return self.context

        gopa, total_opa = self.to_grade_e_total(
            dados=self.get_em_producao()
        )

        ginv, total_inv = self.to_grade_e_total(
            dados=self.get_inventario()
        )

        gsol, total_sol = self.to_grade_e_total(
            dados=self.get_empenhado()
        )

        dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
        self.context.update({
            'dias_alem_lead': dias_alem_lead,
        })

        self.periodo = '' if self.lead == 0 else self.lead + dias_alem_lead

        gped, total_ped = self.to_grade_e_total(
            dados=self.get_grade_pedido(modelo=self.modelo)
        )

        gped, total_ped = self.add_refs_pacote(gped, total_ped)

        self.cortam2context('gme', self.gme)

        self.cortam2context('gmg', self.gmg)

        self.cortam2context('gopa', gopa)

        self.cortam2context('ginv', ginv)

        self.cortam2context('gsol', gsol)

        self.cortam2context('gped', gped)

        tem_meta = abs(self.meta.meta_estoque) + abs(self.meta.meta_giro)
        if tem_meta:
            aux_me = self.gme if self.meta.meta_estoque else self.gzerada
            aux_mg = self.gmg if self.meta.meta_giro else self.gzerada
            gm = self.og.soma_grades(aux_me, aux_mg)
            self.context.update({
                'gm': gm,
            })
        else:
            gm = None

        gopa_ncd = None
        if total_inv != 0:  # and total_opa != total_inv:
            gopa_ncd = self.og.subtrai_grades(gopa, ginv)
            self.context.update({
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
                gresult = self.og.subtrai_grades(gm, gopp)

        glm = None
        glc = None

        if gresult is not None:
            gap = self.og.opera_grade(gresult, lambda x: x if x > 0 else 0)
            self.context.update({
                'gap': gap,
            })
            gex = self.og.opera_grade(gresult, lambda x: -x if x < 0 else 0)
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

        self.cache_set()

        return self.context

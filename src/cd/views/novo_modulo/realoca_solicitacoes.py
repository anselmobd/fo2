import operator
import os
from pathlib import Path
from pprint import pprint, pformat

from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.utils import timezone

from fo2.connections import db_cursor_so

from o2.functions.text import splited
from o2.views.base.get_post import O2BaseGetPostView
from utils.cache import timeout
from utils.functions import (
    coalesce,
    fo2logger,
    my_make_key_cache,
)
from utils.functions.strings import split_numbers
from utils.table_defs import TableDefs
from utils.views import totalize_data

from cd.forms.realoca_solicitacoes import RealocaSolicitacoesForm
from cd.functions import oti_emp
from cd.queries.novo_modulo import (
    refs_em_palets,
    situacao_empenho,
)
from cd.queries.novo_modulo.solicitacao import get_solicitacao
from cd.queries.novo_modulo import situacao_empenho
from cd.queries.novo_modulo import empenho


class RealocaSolicitacoes(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(RealocaSolicitacoes, self).__init__(*args, **kwargs)
        self.Form_class = RealocaSolicitacoesForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/realoca_solicitacoes.html'
        self.title_name = 'Realoca empenhos'

        self.table_defs = TableDefs(
            {
                'palete rota modelo cor lote': [],
                'endereco': ['Endereço'],
                'ref': ['Ref.'],
                'tam': ['Tam.'],
                'op': ['OP'],
                'qtd_prog qtd_lote': ['Tam.Lote', 'r'],
                'qtd_dbaixa': ['Qtd.Est.', 'r'],
                'estagio': ['Estágio', 'c'],
                'solicitacao': ['Solicitação'],
                'pedido_destino': ['Pedido destino'],
                'solicitacoes': ['Solicitações', 'c'],
                'sol_fin': ['Solicit.Fin.', 'c'],
                'sol': ['Solicitação'],
                'qtde': ['Qtd.', 'r'],
                'qtd_emp': ['Qtd.Empen.', 'r'],
                'qtd_sol': ['Qtd.Solic.', 'r'],
                'tot_emp': ['Tot.Empen.', 'r'],
                'qtd_disp': ['Qtd.Disp.', 'r'],
                'qtd_fin': ['Qtd.Fin.', 'r'],
                'sit': ['Situação'],
                'ped_dest': ['Ped.Destino'],
                'ref_dest': ['Ref.Destino'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def get_lotes(self):
        qtd_empenhada = 't' if self.qtd_empenhada == 'ce' else 'nte'
        lotes = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            endereco=self.endereco if self.endereco else "*",
            tipo_prod='pagb',
            qtd_empenhada=qtd_empenhada,
            solicitacoes=self.solicitacoes,
        )
        lotes_a_trabalhar = []
        self.oti_lotes = {}
        for row in lotes:
            row['qtd_dbaixa'] = row['qtd']
            if row['lote'] not in self.lotes_nao_trabalhar:
                lotes_a_trabalhar.append(row)
                self.oti_lotes[row['lote']] = {
                    'end': row['endereco'],
                    'qtde': row['qtd'],
                    'op': row['op'],
                    'oc': row['lote'][4:],
                }
        lotes_a_trabalhar.sort(key=operator.itemgetter('endereco', 'op', 'lote'))
        return lotes_a_trabalhar

    def mount_lotes(self):
        len_lotes = len(self.lotes)
        sum_fields = ['qtd_dbaixa']
        totalize_data(
            self.lotes,
            {
                'sum': sum_fields,
                'descr': {'lote': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )
        fields = [
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
        ]
        self.context['lotes'] = self.table_defs.hfs_dict(*fields)
        self.context['lotes'].update({
            'safe': [
                'op',
                'modelo',
            ],
            'data': self.lotes,
            'len': len_lotes,
        })

    def mount_lotes_disponiveis(self):
        self.lotes = self.get_lotes()
        if len(self.lotes) > 0:
            self.mount_lotes()

    def endereco_selecionado(self, end, selecao):
        if selecao:
            selec_list = splited(selecao)
            for selec in selec_list:
                if len(selec) == 6:
                    if end == selec:
                        return True
                elif '-' in selec:
                    end_de, end_ate = tuple(selec.split('-'))
                    if end >= end_de and end <= end_ate:
                        return True
                else:
                    if end.startswith(selec):
                        return True
        else:
            return end != '-'
        return False

    def add_registros_solis(self, row):
        solis = split_numbers(row['solicitacoes'])
        for sol in solis:
            emps = situacao_empenho.consulta(
                self.cursor,
                ordem_producao=row['op'],
                ordem_confeccao=row['oc'],
                solicitacao=sol,
            )
            self.registros_solis.extend(emps)

    def get_lotes_solis(self):
        empenhos = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            cor=self.cor,
            tam=self.tam,
            modelo=self.modelo,
            tipo_prod='pagb',
            qtd_empenhada=self.qtd_empenhada,
            solicitacoes=self.solicitacoes,
        )
        # só vai trabalhar nos lotes que não estão
        # - já nos endereços desejados; e
        # - com empenhos totais
        empenhos_a_trabalhar = []
        self.lotes_nao_trabalhar = []
        self.registros_solis = []
        for row in empenhos:
            row['qtd_dbaixa'] = row['qtd']
            row['tot_emp'] = row['qtd_emp'] + row['qtd_sol']
            row['qtd_disp'] = row['qtd_dbaixa'] - row['tot_emp']
            end_dest = self.endereco_selecionado(row['endereco'], self.endereco)
            emp_total = row['qtd_disp'] == 0
            trabalha_lote = True
            if emp_total and end_dest and self.trab_sol_tot_dest == 'n':
                trabalha_lote = False
            elif emp_total and self.trab_sol_tot == 'n':
                trabalha_lote = False
            if trabalha_lote:
                empenhos_a_trabalhar.append(row)
                self.add_registros_solis(row)
            else:
                self.lotes_nao_trabalhar.append(row['lote'])
        empenhos_a_trabalhar.sort(key=operator.itemgetter('endereco', 'op', 'lote'))

        self.oti_solicitacoes = {}
        for row in self.registros_solis:
            if row['solicitacao'] not in self.oti_solicitacoes:
                self.oti_solicitacoes[row['solicitacao']] = {
                    'qtde': 0,
                    'pedido_destino': row['pedido_destino'],
                    'op_destino': row['op_destino'],
                    'oc_destino': row['oc_destino'],
                    'situacao': row['situacao'],
                    'grupo_destino': row['grupo_destino'],
                    'alter_destino': row['alter_destino'],
                    'sub_destino': row['sub_destino'],
                    'cor_destino': row['cor_destino'],
                }
            self.oti_solicitacoes[row['solicitacao']]['qtde'] += row['qtde']

        return empenhos_a_trabalhar

    def mount_lotes_solis(self):
        len_lotes_solis = len(self.lotes_solis)
        sum_fields = ['qtd_dbaixa', 'qtd_emp', 'qtd_sol', 'tot_emp', 'qtd_disp']
        totalize_data(
            self.lotes_solis,
            {
                'sum': sum_fields,
                'descr': {'lote': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )
        for row in self.lotes_solis:
            if row['qtd_disp'] < 0:
                row['qtd_disp|STYLE'] = 'color: red;'
        fields = [
            'palete', 'endereco', 'rota',
            'modelo', 'ref', 'tam', 'cor', 'op', 'lote',
            'qtd_prog', 'qtd_dbaixa', 'estagio',
            'solicitacoes', 'qtd_emp', 'qtd_sol', 'tot_emp', 'qtd_disp',
        ]
        self.context['lotes_solis'] = self.table_defs.hfs_dict(*fields)
        self.context['lotes_solis'].update({
            'safe': [
                'op',
                'modelo',
            ],
            'data': self.lotes_solis,
            'len': len_lotes_solis,
        })

    def get_itens(self):
        key_cache = my_make_key_cache(
            'cd/views/novo_modulo/realoca_solicitacoes/get_itens',
            self.qtd_empenhada,
            self.solicitacoes,
        )
        items = cache.get(key_cache)
        if items is not None:
            fo2logger.info('cached '+key_cache)
            return items

        lotes = refs_em_palets.query(
            self.cursor,
            fields='detalhe',
            tipo_prod='pagb',
            qtd_empenhada=self.qtd_empenhada,
            solicitacoes=self.solicitacoes,
        )

        model_qtd_dict = {}
        items_set = set()
        for item in lotes:
            items_set.add((
                item['modelo'],
                item['cor'],
                item['tam'],
                item['ordem_tam'],
            ))
            key = item['modelo']
            if key not in model_qtd_dict:
                model_qtd_dict[key] = {
                    'modelo': item['modelo'],
                    'qtd_sol': 0,
                }
            model_qtd_dict[key]['qtd_sol'] += item['qtd_sol']

        model_qtd = list(model_qtd_dict.values())
        model_qtd.sort(key=operator.itemgetter('qtd_sol'), reverse=True)
        model_ord = [
            row['modelo']
            for row in model_qtd
        ]

        items = [
            {
                'modelo': i[0],
                'cor': i[1],
                'tam': i[2],
                'ordem_tam': i[3],
            }
            for i in items_set
        ]
        items.sort(key=lambda r: (model_ord.index(r['modelo']), r['cor'], r['ordem_tam']))

        cache.set(key_cache, items, timeout=timeout.HOUR)
        fo2logger.info('calculated '+key_cache)

        return items

    def mount_itens(self):
        self.items = self.get_itens()
        self.context['items'] = self.table_defs.hfs_dict(
            'modelo', 'cor', 'tam'
        )
        self.context['items'].update({
            'safe': [
                'modelo',
            ],
            'data': self.items,
            'len': len(self.items),
        })

    def mount_lotes_solicitados(self):
        self.lotes_solis = self.get_lotes_solis()
        self.lista_lotes = [
            row['lote']
            for row in self.lotes_solis
        ]
        if len(self.lotes_solis) > 0:
            self.mount_lotes_solis()

    def get_solis_de_lotes(self):
        dados = get_solicitacao(
            self.cursor,
            solicitacao='!',
            lote=self.lista_lotes,
            situacao=(2, 3, 4),
        )
        return dados

    def get_solis(self):
        self.solis_de_lotes = self.get_solis_de_lotes()
        dados_dict = {}
        for row in self.solis_de_lotes:
            sol = row['solicitacao']
            ped = row['pedido_destino']
            key = (sol, ped)
            if key not in dados_dict:
                dados_dict[key] = 0
            dados_dict[key] += row['qtde']
        dados = [
            {
                'solicitacao': coalesce(key[0], 0),
                'pedido_destino': coalesce(key[1], 0),
                'qtde': qtde,
            }
            for key, qtde in dados_dict.items()
        ]
        dados.sort(key=operator.itemgetter('solicitacao', 'pedido_destino'))
        for row in dados:
            if row['solicitacao'] == 0:
                row['solicitacao'] = '#'
        return dados

    def mount_solis(self):
        len_solis = len(self.solis)
        sum_fields = ['qtde']
        totalize_data(
            self.solis,
            {
                'sum': sum_fields,
                'descr': {'lote': 'Total geral:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )
        fields = [
            'solicitacao', 'pedido_destino', 'qtde'
        ]
        self.context['solis'] = self.table_defs.hfs_dict(*fields)
        self.context['solis'].update({
            'safe': ['solicitacao', 'pedido_destino'],
            'data': self.solis,
            'len': len_solis,
        })

    def mount_solicitacoes(self):
        self.solis = self.get_solis()
        if len(self.solis) > 0:
            self.mount_solis()

    def mount_rascunho_oti(self):
        print("Solicitações")
        pprint(self.oti_solicitacoes)
        total_sols = oti_emp.quant_total(self.oti_solicitacoes)
        print("Total solicitado", total_sols)

        print()
        print("Lotes")
        pprint(self.oti_lotes)
        total_lotes = oti_emp.quant_total(self.oti_lotes)
        print("Total dos lotes", total_lotes)

        qtd_nao_solicitada = total_lotes - total_sols
        print("Quant. não solicitada", qtd_nao_solicitada)

        if qtd_nao_solicitada < 0:
            self.context.update({
                'msg': "Não há quantidade suficiente nos endereços selecionados",
            })
            return

        print()
        print("Inicia nova distribuição")

        print()
        print("Distribuição vazia")
        self.new_lotes_sols =  oti_emp.inicia_distribuicao(self.oti_lotes)
        pprint(self.new_lotes_sols)

        print()
        print("Lotes em ordem decrescente de quantidade")
        lotes_ord = oti_emp.keys_order_by_dict(self.new_lotes_sols, reverse=True)
        pprint(lotes_ord)

        print()
        print("Excluindo lotes a não utilizar")
        oti_emp.lotes_nao_usar(self.new_lotes_sols, lotes_ord, qtd_nao_solicitada)
        pprint(self.new_lotes_sols)

        print()
        print("Lotes atendidos com uma solicitação")
        oti_emp.lotes_uma_sol(self.new_lotes_sols, self.oti_solicitacoes)
        pprint(self.new_lotes_sols)
        pprint(self.oti_solicitacoes.keys())

        print()
        print("Solicitações ordenadas para uso")
        sols_ord = oti_emp.get_sols_ord(self.oti_solicitacoes)
        pprint(sols_ord)

        print()
        print("Lotes em ordem crescente de quantidade")
        lotes_ord.reverse()
        pprint(lotes_ord)

        print()
        print("Empenhar demais lotes")
        self.new_lotes_sols_iter_ord = oti_emp.lotes_parciais(
            self.new_lotes_sols, lotes_ord, sols_ord, self.oti_solicitacoes)

        print()
        print("Visão ordenada dos empenhos otimizados")
        pprint(self.new_lotes_sols_iter_ord)

        print(len(self.new_lotes_sols), "lotes trabalhados", oti_emp.conta_zerados(self.new_lotes_sols), "zerados")

        self.registros_solis_txt = pformat(self.registros_solis)
        self.new_lotes_sols_iter_ord_txt = pformat(self.new_lotes_sols_iter_ord)
        a_fazer = (
            f"Solicitações a cancelar\n\n{self.registros_solis_txt}\n\n"
            f"Solicitações a inserir\n\n{self.new_lotes_sols_iter_ord_txt}"
        )

        self.old_trabalhados = self.context['lotes_solis']['len']
        self.old_zerados = sum((
            row['qtd_disp'] == 0
            for row in self.lotes_solis
        ))
        self.new_trabalhados = len(self.new_lotes_sols)
        self.new_zerados = oti_emp.conta_zerados(self.new_lotes_sols)
        self.context.update({
            'old_trabalhados': self.old_trabalhados,
            'old_zerados': self.old_zerados,
            'new_trabalhados': self.new_trabalhados,
            'new_zerados': self.new_zerados,
        })

        if (
            self.forca_oti == 's'
            or self.new_zerados > self.old_zerados
            or (self.new_zerados == self.old_zerados
                and self.new_trabalhados < self.old_trabalhados
            )
        ):
            self.context.update({
                'a_fazer': a_fazer,
            })

    def filter_inputs(self):
        self.endereco = None if self.endereco == '' else self.endereco
        self.solicitacoes = None if self.solicitacoes == '' else self.solicitacoes
        self.modelo = None if self.modelo == '' else int(self.modelo)
        self.cor = None if self.cor == '' else self.cor
        self.tam = None if self.tam == '' else self.tam
        self.qtd_empenhada = None if self.qtd_empenhada == '' else self.qtd_empenhada
        self.context.update({
            'qtd_empenhada': self.qtd_empenhada,
        })

    def analisa_solicitacoes(self):
        self.mount_itens()

        self.mount_lotes_solicitados()
        if not self.lotes_solis:
            return

        qtd_disp_tot = sum((
            max(row['qtd_disp'], 0)
            for row in self.lotes_solis
        ))
        if self.trab_sol_tot == 'n' and not qtd_disp_tot:
            self.context.update({
                'msg': "Todas as solicitações são totais. Não há o que otimizar.",
            })
            return

        self.mount_solicitacoes()
        self.mount_lotes_disponiveis()
        self.mount_rascunho_oti()

    def grava_alteracoes(self, f):
        f.write(f"situacao_empenho.cancela\n\n")
        for lote_row in self.registros_solis:
            f.write(f"ordem_producao = {lote_row['ordem_producao']}\n")
            f.write(f"ordem_confeccao = {lote_row['ordem_confeccao']}\n")
            f.write(f"pedido_destino = {lote_row['pedido_destino']}\n")
            f.write(f"op_destino = {lote_row['op_destino']}\n")
            f.write(f"oc_destino = {lote_row['oc_destino']}\n")
            f.write(f"grupo_destino = {lote_row['grupo_destino']}\n")
            f.write(f"alter_destino = {lote_row['alter_destino']}\n")
            f.write(f"sub_destino = {lote_row['sub_destino']}\n")
            f.write(f"cor_destino = {lote_row['cor_destino']}\n")
            f.write(f"solicitacao = {lote_row['solicitacao']}\n")
            empenho.exclui(
                self.cursor,
                ordem_producao=lote_row['ordem_producao'],
                ordem_confeccao=lote_row['ordem_confeccao'],
                pedido_destino=lote_row['pedido_destino'],
                op_destino=lote_row['op_destino'],
                oc_destino=lote_row['oc_destino'],
                grupo_destino=lote_row['grupo_destino'],
                alter_destino=lote_row['alter_destino'],
                sub_destino=lote_row['sub_destino'],
                cor_destino=lote_row['cor_destino'],
            )
            f.write("\n")

        f.write("\n")

        f.write("empenho.insere\n")
        for lote, lote_row in self.new_lotes_sols_iter_ord:
            for sol, sol_row in lote_row['sols'].items():
                f.write(f"endereco = {lote_row['end']}\n")
                f.write(f"ordem_producao = {lote_row['op']}\n")
                f.write(f"ordem_confeccao = {lote_row['oc']}\n")
                f.write(f"pedido_destino = {sol_row['pedido_destino']}\n")
                f.write(f"op_destino = {sol_row['op_destino']}\n")
                f.write(f"oc_destino = {sol_row['oc_destino']}\n")
                f.write(f"grupo_destino = {sol_row['grupo_destino']}\n")
                f.write(f"alter_destino = {sol_row['alter_destino']}\n")
                f.write(f"sub_destino = {sol_row['sub_destino']}\n")
                f.write(f"cor_destino = {sol_row['cor_destino']}\n")
                f.write(f"solicitacao = {sol}\n")
                f.write(f"situacao = {sol_row['situacao']}\n")
                f.write(f"qtde = {sol_row['qtde']}\n")
                empenho.insere(
                    self.cursor,
                    ordem_producao=lote_row['op'],
                    ordem_confeccao=lote_row['oc'],
                    pedido_destino=sol_row['pedido_destino'],
                    op_destino=sol_row['op_destino'],
                    oc_destino=sol_row['oc_destino'],
                    grupo_destino=sol_row['grupo_destino'],
                    alter_destino=sol_row['alter_destino'],
                    sub_destino=sol_row['sub_destino'],
                    cor_destino=sol_row['cor_destino'],
                    solicitacao=sol,
                    situacao=sol_row['situacao'],
                    qtde=sol_row['qtde'],
                )
                f.write("\n")

        return

    def executa_alteracoes(self):
        file_dir = "kb/cd/oti_emp/%Y/%m"
        filename = timezone.now().strftime(
            f"{file_dir}/%Y-%m-%d_%H.%M.%S_%f.log")
        Path(os.path.dirname(filename)).mkdir(
                parents=True, exist_ok=True)

        with open(filename, 'w') as f:
            f.writelines(
                map(lambda x: f"{x}\n", [
                    f"endereco: {self.endereco}",
                    f"solicitacoes: {self.solicitacoes}",
                    f"modelo: {self.modelo}",
                    f"cor: {self.cor}",
                    f"tam: {self.tam}",
                    f"qtd_empenhada: {self.qtd_empenhada}",
                    f"forca_oti: {self.forca_oti}",
                    f"old_trabalhados: {self.old_trabalhados}",
                    f"old_zerados: {self.old_zerados}",
                    f"new_trabalhados: {self.new_trabalhados}",
                    f"new_zerados: {self.new_zerados}",
                    f"\nSolicitações a cancelar\n\n{self.registros_solis_txt}\n"
                    f"\nSolicitações a inserir\n\n{self.new_lotes_sols_iter_ord_txt}\n"
                    f"INICIANDO...\n",
                ])
            )

            try:
                with transaction.atomic(using='sn'):
                    self.grava_alteracoes(f)
            except Exception:
                f.write(f"\nERRO\n")
                return False

            f.write(f"\nFINALIZADO\n")
        return True

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)
        self.filter_inputs()

        self.analisa_solicitacoes()
        if 'msg' in self.context:
            return

        if 'otimiza' in self.request.POST:
            self.form.data['forca_oti'] = 'n'
            if self.executa_alteracoes():
                self.context.update({
                    'msg_oti': "Otimização executada.",
                })
            else:
                self.context.update({
                    'msg_oti': "Otimização NÃO executada. Erro!",
                })
            self.analisa_solicitacoes()

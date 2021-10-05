from pprint import pprint

from django.shortcuts import render
from django.urls import reverse

from base.views import O2BaseGetPostView

from fo2.connections import db_cursor_so

import comercial.forms as forms
import comercial.queries as queries


class PlanilhaBling(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PlanilhaBling, self).__init__(*args, **kwargs)
        self.template_name = 'comercial/planilha_bling.html'
        self.title_name = 'Cria planilha Bling'
        self.Form_class = forms.TabelaDePrecoForm
        self.cleaned_data2self = True
        self.colunas = self.init_colunas()

    def gera_linha(self, registro, header=False):
        if header:
            valores = registro.keys()
        else:
            valores = registro.values()
        return ','.join(map(str, valores))

    def mount_context(self):
        self.context.update({
            'tabela': self.tabela
        })

        codigo_tabela_chunks = self.tabela.split('.')
        if len(codigo_tabela_chunks) != 3:
            self.context.update({
                'erro': 'Código inválido. '
                        '3 números inteiros separados por ".".'
            })
            return

        for subcodigo_tabela in codigo_tabela_chunks:
            if not subcodigo_tabela.isdigit():
                self.context.update({
                    'erro': 'Cada subcódigo deve ser um número inteiro.'
                })
                return

        codigo_tabela_ints = list(map(int, codigo_tabela_chunks))

        cursor = db_cursor_so(self.request)

        data = queries.get_tabela_preco(cursor, *codigo_tabela_ints)
        if len(data) == 0:
            self.context.update({
                'erro': 'Tabela não encontrada'
            })
            return

        tabela = data[0]
        for tabela in data:
            tabela['tabela'] = "{:02d}.{:02d}.{:02d}".format(
                tabela['col_tabela_preco'],
                tabela['mes_tabela_preco'],
                tabela['seq_tabela_preco'],
            )
        tabela['tabela|LINK'] = reverse(
            'comercial:tabela_de_preco__get',
            args=[tabela['tabela']]
        )
        tabela['data_ini_tabela'] = tabela['data_ini_tabela'].date()
        tabela['data_fim_tabela'] = tabela['data_fim_tabela'].date()

        self.context.update({
            'headers': [
                'Tabela',
                'Descrição',
                'Início',
                'Fim',
            ],
            'fields': [
                'tabela',
                'descricao',
                'data_ini_tabela',
                'data_fim_tabela',
            ],
            'data': data,
        })

        i_data = queries.itens_tabela_preco_cor_tam(
            cursor, *codigo_tabela_ints)
        if len(i_data) == 0:
            self.context.update({
                'erro': 'Tabela vazia'
            })
            return

        registros = [self.gera_linha(self.colunas, header=True)]
        for row in i_data:
            cor = row["cor"].strip("0")
            codigo = ".".join((row["ref"], row["tam"], cor))
            descr = " - ".join((codigo, row["xref"], row["xtam"], row["xcor"]))
            class_fiscal = "9999.99.99".replace("9", "{}").format(*row["cfiscal"])

            registro = self.colunas.copy()
            registro.update({
                "Codigo": codigo,
                "Descricao": descr,
                "Classificacao_fiscal": class_fiscal,
                "Preco": row["preco"],
                "Peso_liquido_kg": row["pesol"],
                "Peso_bruto_kg": row["pesol"],
                "GTIN_EAN": row["gtin"],
                "Código Pai": "",  # Sem código pai
            })

            registros.append(
                self.gera_linha(registro)
            )

        self.context['planilha'] = "\n".join(registros)
        self.context['planilha_download'] = "%0D%0A".join(
            [r.replace(" ", "%20") for r in registros]
        )
        self.context['file_name'] = f"produtos_{tabela['tabela']}.csv"

    def init_colunas(self):
        return {
            "ID": "",
            "Codigo": "",
            "Descricao": "",
            "Unidade": "UN",
            "Classificacao_fiscal": "",
            "Origem": 0,
            "Preco": "",
            "Valor_IPI_fixo": 0,
            "Observacoes": "",
            "Situacao": "Ativo",
            "Estoque": 100000,
            "Preco_de_custo": 0,
            "Cod_no_fornecedor": "",
            "Fornecedor": "",
            "Localizacao": "",
            "Estoque_maximo": 0,
            "Estoque_minimo": 0,
            "Peso_liquido_kg": "",
            "Peso_bruto_kg": "",
            "GTIN_EAN": "",
            "GTIN_EAN_da_ embalagem": "",
            "Largura_do_ Produto": 35.5,
            "Altura_do_Produto": 25.5,
            "Profundidade_do_produto": 4.5,
            "Data_Validade": "",
            "Descricao_do_Produto_no_Fornecedor": "",
            "Descricao_Complementar": "",
            "Unidade_por_Caixa": 1,
            "Produto_Variacao": "Produto",
            "Tipo_Producao": "Própria",
            "Classe_de_enquadramento_do_IPI": "",
            "Codigo_da_lista_de_servicos": "",
            "Tipo_do_item": "",
            "Grupo de Tags/Tags": "",
            "Tributos": 0,
            "Código Pai": "",
            "Código Integração": 0,
            "Grupo de Produtos": "",
            "Marca": "DUOMO",
            "CEST": "",
            "Volumes": 0,
            "Descriçãoo curta": "",
            "Cross-Docking": 0,
            "URL Imagens Externas": "",
            "Link Externo": "",
            "Meses Garantia": "",
            "Clonar dados do pai": "NÃO",
            "Condição do produto": "NOVO",
            "Frete Grátis": "SIM",
            "Número FCI": "",
            "Vídeo": "",
            "Departamento": "",
            "Unidade de medida": "Centímetro",
            "Preço de compra": 0,
            "Valor base ICMS ST para retenÃ§Ã£o": 0,
            "Valor ICMS ST para retenção": 0,
            "Valor ICMS próprio do substituto": 0,
            "Categoria do produto": "ROUPA INTIMA"
        }

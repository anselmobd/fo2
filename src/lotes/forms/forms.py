from pprint import pprint
from datetime import datetime, timedelta

from django import forms

from produto.models import ProdutoItem
from systextil.models import Colecao, Familia


class LoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote/OC', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class OpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

class HistoricoOpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    oc = forms.CharField(
        label='OC', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    dia = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    usuario = forms.CharField(
        label='Usuário', max_length=20, required=False,
        widget=forms.TextInput(attrs={
            'type': 'string',
            'style': 'text-transform:uppercase;',
        }))
    descr = forms.CharField(
        label='Partes da descrição', max_length=30, required=False,
        widget=forms.TextInput(attrs={
            'type': 'string',
            'style': 'text-transform:uppercase;',
        }))
    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario'].upper()
        data = self.data.copy()
        data['usuario'] = usuario
        self.data = data
        return usuario

    def clean_descr(self):
        descr = self.cleaned_data['descr'].upper()
        data = self.data.copy()
        data['descr'] = descr
        self.data = data
        return descr


class OsForm(forms.Form):
    os = forms.CharField(
        label='OS',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class PeriodoAlterForm(forms.Form):
    periodo_de = forms.CharField(
        label='Período: De',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    periodo_ate = forms.CharField(
        label='Até', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    alternativa = forms.CharField(
        label='Alternativa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_periodo(self, periodo):
        try:
            i_periodo = int(float(periodo))
            if i_periodo < 0:
                periodo = None
        except ValueError:
            periodo = None
        return periodo

    def clean_periodo_de(self):
        return self.clean_periodo(self.cleaned_data['periodo_de'])

    def clean_periodo_ate(self):
        return self.clean_periodo(self.cleaned_data['periodo_ate'])


class DtCorteAlterForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De',
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    alternativa = forms.CharField(
        label='Alternativa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    # roteiro = forms.CharField(
    #     label='Roteiro', required=False,
    #     widget=forms.TextInput(attrs={'type': 'number'}))

    # tipo = forms.CharField(
    #     label='Tipo (MD, PG, PA)', required=False, widget=forms.TextInput)

    # def clean_tipo(self):
    #     tipo = self.cleaned_data['tipo'].upper()
    #     if tipo not in ('MD', 'PG', 'PA'):
    #         tipo = ''
    #     return tipo


class ResponsPorEstagioForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    usuario = forms.CharField(
        label='Usuário', max_length=20, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    CHOICES = [('e', 'Por estágio'),
               ('u', 'Por usuário')]
    ordem = forms.ChoiceField(
        choices=CHOICES, initial='e', widget=forms.RadioSelect())

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario'].upper()
        data = self.data.copy()
        data['usuario'] = usuario
        self.data = data
        return usuario


class ImprimePacote3LotesForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    ultimo = forms.CharField(
        label='Lote em última etiqueta de caixa impressa', required=False,
        max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number'}))
    ultima_cx = forms.CharField(
        label='Número da última caixa impressa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    pula = forms.IntegerField(
        label='Pula quantos pacotes', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    qtd_lotes = forms.IntegerField(
        label='Imprime quantos pacotes', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    CHOICES = [('B', 'Etiqueta de caixa com barras de 3 lotes'),
               ('C', 'Etiqueta de caixa de lotes')]
    impresso = forms.ChoiceField(
        label='Impresso', choices=CHOICES, initial='B')
    obs1 = forms.CharField(
        label='Observação 1', required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'style': 'width:20en'}))
    obs2 = forms.CharField(
        label='Observação 2', required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'style': 'width:20en'}))

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class OpPendenteForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    periodo_de = forms.CharField(
        label='Período: De', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    periodo_ate = forms.CharField(
        label='Até', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    colecao = forms.ModelChoiceField(
        label='Coleção', required=False,
        queryset=Colecao.objects.exclude(colecao=0).order_by(
            'colecao'), empty_label="(Todas)")

    CHOICES = [('-', 'Ambas (2 e 4)'),
               ('2', '2 - Ordem confecção gerada'),
               ('4', '4 - Ordens em produção')]
    situacao = forms.ChoiceField(
        label='Situação', choices=CHOICES, initial='0')

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        label='Tipo de produto', choices=CHOICES, initial='t')

    def clean_periodo(self, periodo, default):
        try:
            i_periodo = int(float(periodo))
            if i_periodo < 0:
                periodo = default
        except ValueError:
            periodo = default
        return periodo

    def clean_periodo_de(self):
        return self.clean_periodo(self.cleaned_data['periodo_de'], 0)

    def clean_periodo_ate(self):
        return self.clean_periodo(self.cleaned_data['periodo_ate'], 9999)

    def clean_situacao(self):
        if self.cleaned_data['situacao'] == '-':
            return ''
        else:
            return self.cleaned_data['situacao']


class ModeloTermicaForm(forms.ModelForm):
    gabarito = forms.CharField(
        label='Gabarito',
        widget=forms.Textarea(
            attrs={'max_length': 8192, 'rows': 20, 'cols': 79}))


class DistribuicaoForm(forms.Form):
    # estagio = forms.CharField(
    #     label='Estágio', max_length=2, required=False,
    #     widget=forms.TextInput(attrs={'type': 'number',
    #                            'autofocus': 'autofocus'}))
    data_de = forms.DateField(
        label='Data da distribuição: De',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    familia = forms.ModelChoiceField(
        label='Família (tear)', required=False,
        queryset=Familia.objects.filter(
            divisao_producao__range=['3000', '3999']).order_by(
            'divisao_producao'), empty_label="(Todas)")

    # def clean_estagio(self):
    #     estagio = self.cleaned_data['estagio']
    #     if estagio == '':
    #         estagio = '22'
    #     data = self.data.copy()
    #     data['estagio'] = estagio
    #     self.data = data
    #     return estagio


class BuscaOpForm(forms.Form):
    ref = forms.CharField(
        label='Referência', required=False, min_length=1, max_length=5,
        help_text='(aceita filtro com "%")',
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))
    modelo = forms.CharField(
        label='Modelo', max_length=4, min_length=1, required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    deposito = forms.CharField(
        label='Depósito', required=False, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cnpj9 = forms.CharField(
        label='Início do CNPJ', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [('qq', 'Qualquer'),
               ('15', 'Corte'),
               ('22', 'Tecelagem'),
               ]
    estagio_op = forms.ChoiceField(
        label='OP com estágio', choices=CHOICES, initial='qq')

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        label='Tipo de produto', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas'),
               ('p', 'Alternativa de produção'),
               ('e', 'Alternativa de expedição'),
               ]
    tipo_alt = forms.ChoiceField(
        label='Tipo de alternativa', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('a', 'Ativas'),
               ('c', 'Canceladas'),
               ]
    situacao = forms.ChoiceField(
        label='Situação da OP', choices=CHOICES, initial='a')

    CHOICES = [
        ('v', 'Estágios 60, 57, 63, 64 e 66'),
        ('s', 'Somente estágio 63'),
    ]
    estagios_cd = forms.ChoiceField(
        label='Estágios considerados como CD', choices=CHOICES, initial='v')

    CHOICES = [('t', 'Todas as OPs'),
               ('p', 'Em produção'),
               ('f', 'Finalizadas'),
               ('pcd', 'Em produção, exceto OPs apenas no CD'),
               ('fcd', 'Finalizadas, incluindo OPs apenas no CD'),
               ]
    posicao = forms.ChoiceField(
        label='Posição da produção', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('e', 'OP de estoque'),
               ('p', 'OP de pedido (qualquer)'),
               ('n', 'OP de pedido não faturado'),
               ('f', 'OP de pedido faturado'),
               ('c', 'OP de pedido faturado e cancelado'),
               ('d', 'OP de pedido faturado e devolvido'),
               ('a', 'OP de pedido faturável '
                     '(não faturado ou faturado e cancelado)'),
               ('i', 'OP de pedido não faturável '
                     '(faturado ou faturado e devolvido)'),
               ]
    motivo = forms.ChoiceField(
        label='Motivo da OP', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('z', 'Zerada'),
               ('n', 'Não zerada'),
               ]
    quant_fin = forms.ChoiceField(
        label='Quantidade finalizada', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('z', 'Zerada'),
               ('n', 'Não zerada'),
               ]
    quant_emp = forms.ChoiceField(
        label='Quantidade em produção', choices=CHOICES, initial='t')

    data_de = forms.DateField(
        label='Data do Corte: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    apenas_totais = forms.BooleanField(
        label='Apenas totais', required=False,
        widget=forms.CheckboxInput(attrs={'checked': False}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class TotaisEstagioForm(forms.Form):
    CHOICES = [('p', 'De produção'),
               ('e', 'De expedição'),
               ('t', 'Todos'),
               ]
    tipo_roteiro = forms.ChoiceField(
        label='Tipo de roteiro de OP',
        choices=CHOICES, required=False, initial='p')

    cliente = forms.CharField(
        label='Produtos do cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    deposito = forms.CharField(
        label='Depósito', required=False, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].upper()
        data = self.data.copy()
        data['cliente'] = cliente
        self.data = data
        return cliente


class QuantEstagioForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    ref = forms.CharField(
        label='Referência', required=False, min_length=1, max_length=5,
        help_text='(aceita filtro com "%")',
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        choices=CHOICES, required=False, initial='t')

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class ImprimeOb1Form(forms.Form):
    os = forms.IntegerField(
        label='OS',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    caixa_inicial = forms.IntegerField(
        label='Caixa inicial', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    caixa_final = forms.IntegerField(
        label='Caixa final', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

from django import forms

from base.forms import O2BaseForm, O2FieldRefForm, O2FieldModeloForm, O2FieldClienteForm
from utils.functions import mes_atual, ano_atual


class ClienteForm(forms.Form):
    cnpj = forms.CharField(
        label='CNPJ (início) ou Razão Social (parte)',
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


class VendasForm(
        O2BaseForm,
        O2FieldRefForm,
        O2FieldModeloForm):

    CHOICES = [
        ('ref', 'Referência'),
        ('modelo', 'Modelo'),
        ('tam', 'Tamanho'),
        ('cor', 'Cor'),
        ('nf', 'Nota fiscal'),
    ]
    infor = forms.ChoiceField(
        label='Informação', choices=CHOICES, initial='ref')

    CHOICES = [
        ('venda', 'Apenas com venda no período'),
        ('tudo', 'Com e sem venda no período'),
    ]
    lista = forms.ChoiceField(
        label='Lista Informação', choices=CHOICES, initial='venda')

    CHOICES = [
        ('infor', 'Informação'),
        ('qtd', 'Quantidade'),
    ]
    ordem = forms.ChoiceField(
        label='Ordem', choices=CHOICES, initial='infor')

    CHOICES = [
        ('0', 'Total vendido'),
        ('a123', 'Mês atual e 3 anteriores'),
        ('3612', '3 e 6 meses, 1 e 2 anos'),
        ('meta', 'Períodos de análises de metas'),
    ]
    periodo = forms.ChoiceField(
        label='Períodos em colunas', choices=CHOICES, initial='0')

    CHOICES = [
        ('t', 'Total do período'),
        ('m', 'Média por mês'),
    ]
    qtd_por_mes = forms.ChoiceField(
        label='Quantidades', choices=CHOICES, initial='t')

    class Meta:
        autofocus_field = 'ref'
        order_fields = [
            'ref',
            'modelo',
            'infor',
            'ordem',
            'lista',
            'periodo',
            'qtd_por_mes',
        ]


class VendasPorForm(
        O2BaseForm,
        O2FieldRefForm):

    # cliente = forms.CharField(
    #     required=False,
    #     help_text='CNPJ (início) ou Razão Social (parte)',
    #     widget=forms.TextInput({'autofocus': 'autofocus'}))

    def __init__(self, *args, **kwargs):
        super(VendasPorForm, self).__init__(*args, **kwargs)
        self.order_fields([
            # 'cnpj',
            'ref',
        ])


class DevolucaoParaMetaForm(
        O2BaseForm,
        O2FieldRefForm):
    ano = forms.IntegerField(
        required=False, initial=ano_atual,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

    mes = forms.IntegerField(required=False, initial=mes_atual)

    CHOICES = [
        ('cliente', 'Por cliente'),
        ('detalhe', 'Por nota'),
        ('referencia', 'Por nota e referência'),
        ]
    apresentacao = forms.ChoiceField(
        choices=CHOICES, initial='cliente', label='Apresentação')

    class Meta:
        autofocus_field = 'ano'
        order_fields = [
            'ano',
            'mes',
            'ref',
            'apresentacao',
        ]


class FaturamentoParaMetaForm(
        O2BaseForm,
        O2FieldRefForm,
        O2FieldClienteForm):

    ano = forms.IntegerField(
        required=False, initial=ano_atual,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

    mes = forms.IntegerField(required=False, initial=mes_atual)

    CHOICES = [
        ('mes', 'Por mês'),
        ('nota', 'Por nota'),
        ('nota_referencia', 'Por nota e referência'),
        ('cliente', '*Por cliente'),
        ('referencia', '*Por referência'),
        ('modelo', '*Por modelo'),
        ]
    apresentacao = forms.ChoiceField(
        choices=CHOICES, initial='mes', label='Apresentação')

    CHOICES = [
        ('apresentacao', 'Pela informação da apresentação'),
        ('valor', '*Pelo valor'),
        ]
    ordem = forms.ChoiceField(
        choices=CHOICES, initial='apresentacao')

    class Meta:
        autofocus_field = 'ano'
        order_fields = [
            'ano',
            'mes',
            'ref',
            'cliente',
            'apresentacao',
            'ordem',
        ]


class TabelaDePrecoForm(forms.Form):
    tabela = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'autofocus': 'autofocus'}
        )
    )

    def clean_tabela(self):
        tabela = self.cleaned_data['tabela'].upper()
        data = self.data.copy()
        data['tabela'] = tabela
        self.data = data
        return tabela

from django import forms

from base.forms import O2BaseForm, O2FieldRefForm, O2FieldModeloForm
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
        label='Informação totalizada', choices=CHOICES, initial='ref')

    CHOICES = [
        ('venda', 'Apenas com venda'),
        ('tudo', 'Com e sem venda'),
    ]
    lista = forms.ChoiceField(
        label='Lista Informação', choices=CHOICES, initial='venda')

    CHOICES = [
        ('infor', 'Informação totalizada'),
        ('qtd', 'Quantidade'),
    ]
    ordem = forms.ChoiceField(
        label='Ordem', choices=CHOICES, initial='infor')

    CHOICES = [
        ('0', 'Total'),
        ('a123', 'Mês atual e 3 anteriores'),
        ('3612', '3 e 6 meses, 1 e 2 anos'),
        ('meta', 'Períodos de análises de metas'),
    ]
    periodo = forms.ChoiceField(
        label='Períodos em colunas', choices=CHOICES, initial='0')

    CHOICES = [
        ('t', 'Totais'),
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
            'lista',
            'ordem',
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


class FaturamentoParaMetaForm(
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

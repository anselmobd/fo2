from django import forms

from base.forms.custom import O2BaseForm
from base.forms.fields import (
    O2FieldClienteForm,
    O2FieldCorForm,
    O2FieldModeloForm,
    O2FieldReferenciaForm,
    O2FieldTamanhoForm,
)
from utils.functions import mes_atual, ano_atual

from systextil.models import Colecao
from systextil.models.base import Empresa


class ClienteForm(forms.Form):
    cnpj = forms.CharField(
        label='CNPJ (início) ou Razão Social (parte)',
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


class VendasForm(
        O2BaseForm,
        O2FieldReferenciaForm,
        O2FieldModeloForm):

    colecao = forms.ModelChoiceField(
        label='Coleção da referência', required=False,
        queryset=Colecao.objects.all().order_by(
            'colecao'), empty_label="(Todas)")

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
        ('atual', 'Mês atual'),
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
            'colecao',
            'infor',
            'ordem',
            'lista',
            'periodo',
            'qtd_por_mes',
        ]


class VendasPorForm(
        O2BaseForm,
        O2FieldReferenciaForm):

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
        O2FieldReferenciaForm):
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
        O2FieldReferenciaForm,
        O2FieldTamanhoForm,
        O2FieldCorForm,
        O2FieldClienteForm):

    empresa_choices = []

    empresa = forms.ChoiceField(
        required=True, initial=None)

    ano = forms.IntegerField(
        required=False,
        initial=ano_atual,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}),
    )

    mes = forms.IntegerField(required=False, initial=mes_atual)

    colecao = forms.ModelChoiceField(
        label='Coleção da referência',
        required=False,
        queryset=Colecao.objects.all().order_by('colecao'),
        empty_label="(Todas)",
    )

    CHOICES = [
        ('mes', 'Por mês'),
        ('nota', 'Por nota'),
        ('nota_referencia', 'Por nota e referência'),
        ('cliente', '*Por cliente'),
        ('referencia', '*Por referência'),
        ('modelo', '*Por modelo'),
        ('colecao', '*Por coleção'),
    ]
    apresentacao = forms.ChoiceField(
        label='Apresentação',
        choices=CHOICES,
        initial='mes',
    )

    CHOICES = [
        ('apresentacao', 'Pela informação da apresentação'),
        ('valor', '*Pelo valor'),
        ('qtd', '*Pela quantidade'),
    ]
    ordem = forms.ChoiceField(
        choices=CHOICES,
        initial='apresentacao',
    )

    CHOICES = [
        ('canceladas', 'Apenas canceladas'),
        ('devolvidas', 'Canceladas e devolvidas'),
    ]
    exclui = forms.ChoiceField(
        choices=CHOICES,
        initial='canceladas',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.empresa_choices:
            empresas = Empresa.objects.all().order_by('codigo_empresa')
            for empresa in empresas:
                self.empresa_choices.append((
                    str(empresa.codigo_empresa),
                    f"{empresa.codigo_empresa}-{empresa.nome_fantasia}",
                ))
        self.fields['empresa'].choices = self.empresa_choices

    class Meta:
        autofocus_field = 'ano'
        order_fields = [
            'empresa',
            'ano',
            'mes',
            'ref',
            'tamanho',
            'cor',
            'colecao',
            'cliente',
            'apresentacao',
            'ordem',
            'exclui',
        ]


class PedidosParaMetaForm(forms.Form):
    ano = forms.IntegerField(
        required=False, initial=ano_atual,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

    mes = forms.IntegerField(required=False, initial=mes_atual)


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

class NfEspecialForm(forms.Form):
    nf = forms.IntegerField(
        label='NF',
        required=True,
        widget=forms.NumberInput(
            attrs={'autofocus': 'autofocus'}
        ),
    )


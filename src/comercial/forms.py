from django import forms

from base.forms import O2BaseForm, O2FieldRefForm
from utils.functions import mes_atual, ano_atual


class ClienteForm(forms.Form):
    cnpj = forms.CharField(
        label='CNPJ (início) ou Razão Social (parte)',
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


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


class FaturamentoParaMetaForm(forms.Form):
    ano = forms.IntegerField(
        required=False, initial=ano_atual,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

    mes = forms.IntegerField(required=False, initial=mes_atual)

    CHOICES = [
        ('C', 'Por cliente'),
        ('N', 'Por nota'),
        ]
    apresentacao = forms.ChoiceField(
        choices=CHOICES, initial='C', label='Apresentação')


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

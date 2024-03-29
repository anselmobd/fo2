from pprint import pprint

from django import forms

from base.forms.custom import O2BaseForm
from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.gtin import gtin_check_digit
from utils.functions.strings import re_split_non_empty

from produto.functions import fill_ref


class O2FieldNivelForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', min_value=1, max_value=9,
        required=False,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 1}))


class O2FieldNivelReqForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', min_value=1, max_value=9,
        required=True,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 1}))


class O2FieldModeloForm(forms.Form):
    modelo = forms.IntegerField(
        min_value=1, max_value=99999,
        required=False,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 5}))


class O2FieldRefForm(forms.Form):
    ref = forms.CharField(
        label='Referência',
        required=False,
        widget=forms.TextInput(attrs={'size': 5}))

    def clean_ref(self):
        return O2BaseForm.cleanner_pad(self, 'ref', 5)


class O2FieldReferenciaForm(forms.Form):

    ref = forms.CharField(
        label='Referência',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **FormWidgetAttrs().string_upper,
                **FormWidgetAttrs().placeholder_0,
            }
        )
    )

    def clean_ref(self):
        data = self.data.copy()
        data['ref'] = fill_ref(self.cleaned_data['ref'])
        self.data = data
        return data['ref']


class O2FieldReceitaForm(forms.Form):
    receita = forms.CharField(
        label='Receita',
        required=False, min_length=5, max_length=5,
        widget=forms.TextInput(attrs={'size': 5}))

    def clean_receita(self):
        return O2BaseForm.upper(self, 'receita')


class O2FieldItemForm(forms.Form):

    def __init__(self, *args, nivel='1', **kwargs):
        super(O2FieldItemForm, self).__init__(*args, **kwargs)
        self.nivel = nivel

    item = forms.CharField(
        required=False,
        max_length=18,
        widget=forms.TextInput(
            attrs={
                'size': 18,
                **FormWidgetAttrs().string_upper,
                **FormWidgetAttrs().placeholder_item,
            }
        )
    )  # 1.12345.123.123456

    def clean_item(self):
        item = self.cleaned_data['item'].upper()
        data = self.data.copy()
        parts = re_split_non_empty(item, '. ')
        if len(parts) == 1:  ## 112345123123456
            if len(item) < 15:
                item = f"{self.nivel}{item}"
            parts = [
                item[0],
                item[1:6],
                item[6:-6],
                item[-6:],
            ]
        else:
            if len(parts) == 3:
                parts.insert(0, self.nivel)
            try:
                parts[1] = fill_ref(parts[1])
            except:
                pass
            parts[3] = parts[3].zfill(6)
        item = '.'.join(parts)
        data['item'] = item
        self.data = data
        return item


class O2FieldReceitaItemForm(O2FieldItemForm):

    def __init__(self, *args, **kwargs):
        super(O2FieldReceitaItemForm, self).__init__(*args, nivel='5', **kwargs)


class O2FieldClienteForm(forms.Form):
    cliente = forms.CharField(
        label='Cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    def clean_cliente(self):
        return O2BaseForm.upper(self, 'cliente')


class O2FieldTamanhoForm(forms.Form):
    tamanho = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 3}))

    def clean_tamanho(self):
        return O2BaseForm.cleanner(self, 'tamanho')


class O2FieldCorForm(forms.Form):
    cor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 6}))

    def clean_cor(self):
        return O2BaseForm.cleanner_pad(self, 'cor', 6)


class O2FieldGtinForm(forms.Form):
    gtin = forms.CharField(
        label='GTIN', max_length=13, min_length=12, required=False,
        widget=forms.TextInput(attrs={'size': 13}))

    def clean_gtin(self):
        gtin = O2BaseForm.cleanner(self, 'gtin', field_type='n')
        if len(gtin) == 12:
            gtin += gtin_check_digit(gtin)
        return gtin


class O2FieldFiltroForm(forms.Form):
    filtro = forms.CharField(
        required=False,
        help_text='Busca vários valores separados por espaço.',
        widget=forms.TextInput())

    def clean_filtro(self):
        return O2BaseForm.upper(self, 'filtro')

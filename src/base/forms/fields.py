from pprint import pprint

from django import forms

from base.forms import O2BaseForm


class O2FieldNivelForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', min_value=1, max_value=9,
        required=False,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 1}))


class O2FieldRefForm(forms.Form):
    ref = forms.CharField(
        label='Referência',
        required=False,
        widget=forms.TextInput(attrs={'size': 5}))

    def clean_ref(self):
        return O2BaseForm.cleanner_pad(self, 'ref', 5)


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
        label='GTIN', max_length=13, min_length=13, required=False,
        widget=forms.TextInput(attrs={'size': 13}))

    def clean_cor(self):
        return O2BaseForm.cleanner(self, 'gtin')


class O2FieldFiltroForm(forms.Form):
    filtro = forms.CharField(
        required=False,
        help_text='Busca vários valores separados por espaço.',
        widget=forms.TextInput())

    def clean_filtro(self):
        return O2BaseForm.upper(self, 'filtro')

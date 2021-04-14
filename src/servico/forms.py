from django import forms

from base.forms import O2BaseForm


class O2FieldOrdemForm(forms.Form):
    ordem = forms.IntegerField(
        min_value=0, max_value=999999,
        required=False, initial='0',
        widget=forms.TextInput(attrs={'type': 'number', 'size': 6}))


class OrdensForm(
        O2BaseForm,
        O2FieldOrdemForm):

    class Meta:
        autofocus_field = 'ordem'


class CriaOrdemForm(
        O2BaseForm):

    descricao = forms.CharField(
        label='Descrição', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    class Meta:
        autofocus_field = 'descricao'

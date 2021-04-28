from django import forms
from django.forms import ModelForm

from base.forms import O2BaseForm

from servico.models import Interacao


class O2FieldDocumentoForm(forms.Form):
    documento = forms.IntegerField(
        min_value=1, max_value=999999,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 6}))


class O2FiltraOrdemForm(forms.Form):
    ordem = forms.IntegerField(
        min_value=0, max_value=999999,
        required=False, initial='0',
        widget=forms.TextInput(attrs={'type': 'number', 'size': 6}))


class OrdemForm(
        O2BaseForm,
        O2FieldDocumentoForm):

    class Meta:
        autofocus_field = 'documento'


class ListaForm(
        O2BaseForm,
        O2FiltraOrdemForm):

    class Meta:
        autofocus_field = 'ordem'


class CriaInteracaoForm(ModelForm):
    class Meta:
        model = Interacao
        fields = ['equipe', 'descricao', 'nivel']

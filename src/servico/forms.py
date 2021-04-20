from django import forms
from django.forms import ModelForm

from base.forms import O2BaseForm

from servico.models import ServicoEvento


class O2FieldOrdemForm(forms.Form):
    numero = forms.IntegerField(
        min_value=1, max_value=999999,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 6}))


class O2FiltraOrdemForm(forms.Form):
    ordem = forms.IntegerField(
        min_value=0, max_value=999999,
        required=False, initial='0',
        widget=forms.TextInput(attrs={'type': 'number', 'size': 6}))


class OrdemForm(
        O2BaseForm,
        O2FieldOrdemForm):

    class Meta:
        autofocus_field = 'numero'


class OrdensForm(
        O2BaseForm,
        O2FiltraOrdemForm):

    class Meta:
        autofocus_field = 'ordem'


class CriaServicoEventoForm(ModelForm):
    class Meta:
        model = ServicoEvento
        fields = ['equipe', 'descricao', 'nivel']

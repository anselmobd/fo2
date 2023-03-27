from pprint import pprint

from django import forms

from systextil.models import Colecao


class LeadColecaoForm(forms.Form):
    lead = forms.IntegerField(
        required=False, min_value=0, max_value=100,
        widget=forms.TextInput(attrs={'type': 'number'}))


class LoteMinColecaoForm(forms.Form):
    lm_tam = forms.IntegerField(
        label='Lote mínimo por tamanho',
        required=False, min_value=0, max_value=10000,
        widget=forms.TextInput(attrs={'type': 'number'}))

    lm_cor = forms.IntegerField(
        label='Lote mínimo por cor',
        required=False, min_value=0, max_value=10000,
        widget=forms.TextInput(attrs={'type': 'number'}))


class LoteCaixaAddForm(forms.Form):
    colecao = forms.ModelChoiceField(
        label='Coleção', required=True,
        queryset=Colecao.objects.exclude(colecao=0).order_by('colecao'))

    referencia = forms.CharField(
        label='Referência', required=False, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={
            'type': 'string',
            'style': 'text-transform:uppercase;',
        }))

    lotes_caixa = forms.IntegerField(
        label='Lotes por caixa',
        min_value=0, max_value=10,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_referencia(self):
        referencia = self.cleaned_data['referencia'].upper()
        data = self.data.copy()
        data['referencia'] = referencia
        self.data = data
        return referencia


class LoteCaixaForm(forms.Form):
    lotes_caixa = forms.IntegerField(
        label='Lotes por caixa',
        min_value=0, max_value=10,
        widget=forms.TextInput(attrs={'type': 'number'}))


class RegrasLoteMinTamanhoForm(forms.Form):
    min_para_lm = forms.IntegerField(
        label='% mínimo para aplicação do lote mínimo por tamanho',
        required=False, min_value=0, max_value=100,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    lm_cor_sozinha = forms.ChoiceField(
        label='Aplica lote mínimo por cor quando único tamanho',
        choices=CHOICES, required=False, initial='s')

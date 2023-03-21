from pprint import pprint
from datetime import datetime

from django import forms

from utils.functions.functions import inc_dias_mes_menos1

from systextil.models import Colecao


__all__ = ['OpPerdaForm']


class OpPerdaForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Corte: De', required=False,
        help_text='Padrão: Hoje',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'value': datetime.now().date()}))
    data_ate = forms.DateField(
        label='Até', required=False,
        help_text='Padrão: Período de um mês',
        widget=forms.DateInput(attrs={'type': 'date'}))

    colecao = forms.ModelChoiceField(
        label='Coleção da referência', required=False,
        queryset=Colecao.objects.exclude(colecao=0).order_by(
            'colecao'), empty_label="(Todas)")

    CHOICES = [
        ('ref', 'Por referência'),
        ('item', 'Por referência-cor-tamanho'),
        ('col', 'Por coleção'),
    ]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='ref')

    def clean_data_de(self):
        data_de = self.cleaned_data['data_de']
        if data_de is None:
            data_de = datetime.now().date()
            data = self.data.copy()
            data['data_de'] = data_de
            self.data = data
        return data_de

    def clean_data_ate(self):
        data_ate = self.cleaned_data['data_ate']
        if data_ate is None:
            data_ate = inc_dias_mes_menos1(self.cleaned_data['data_de'])
            data = self.data.copy()
            data['data_ate'] = data_ate
            self.data = data
        return data_ate

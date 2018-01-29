from datetime import datetime, timedelta

from django import forms


class NotafiscalRelForm(forms.Form):

    def data_ini():
        return (datetime.now().replace(day=1)-timedelta(days=1)).replace(day=1)

    data_de = forms.DateField(
        label='Data do Faturamento: De', required=False,
        initial=data_ini,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    uf = forms.CharField(
        label='UF', max_length=2, min_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'char', 'size': 2}))

    nf = forms.CharField(
        label='Número da NF', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    cliente = forms.CharField(
        label='Cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    transportadora = forms.CharField(
        label='Transportadora', required=False,
        help_text='Sigla da transportadora.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('N', 'Não filtra'),
               ('C', 'Com data de saída informada'),
               ('S', 'Sem data de saída')]
    data_saida = forms.ChoiceField(
        label='Quanto a data de saída', choices=CHOICES, initial='S')

    CHOICES = [('N', 'Número da nota fiscal'),
               ('A', 'Atraso (maior primeiro)')]
    ordem = forms.ChoiceField(
        label='Ordem de apresentação', choices=CHOICES, initial='A')

    def clean_uf(self):
        uf = self.cleaned_data['uf'].upper()
        data = self.data.copy()
        data['uf'] = uf
        self.data = data
        return uf

    def clean_data_de(self):
        data_de = self.cleaned_data['data_de']
        if data_de.year < 100:
            data_de = data_de.timedelta(years=2000)
        return data_de

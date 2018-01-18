from django import forms


class NotafiscalRelForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Faturamento: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'size': 10,
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Data do Faturamento: Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'size': 10}))

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

    CHOICES = [('A', 'Ambas'),
               ('S', 'Sim'),
               ('N', 'Não')]
    data_saida = forms.ChoiceField(
        label='Com data de saída?', choices=CHOICES, initial='A')

    def clean_uf(self):
        uf = self.cleaned_data['uf'].upper()
        data = self.data.copy()
        data['uf'] = uf
        self.data = data
        return uf

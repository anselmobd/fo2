from django import forms


class NotafiscalRelForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Faturamento: De',
        widget=forms.DateInput(attrs={'type': 'date', 'size': 10,
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'size': 10}))

    uf = forms.CharField(
        label='UF', max_length=2, min_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'char', 'size': 2}))

    def clean_uf(self):
        uf = self.cleaned_data['uf'].upper()
        data = self.data.copy()
        data['uf'] = uf
        self.data = data
        return uf

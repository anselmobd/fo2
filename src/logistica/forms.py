from django import forms


class NotafiscalRelForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Faturamento: De',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

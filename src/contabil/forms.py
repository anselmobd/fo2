from django import forms


class InfAdProdForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class RemessaIndustrForm(forms.Form):
    data_de = forms.DateField(
        label='Data inicial', required=True,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='Data final', required=False,
        help_text='(Se não informar, assume igual a inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))

    faccao = forms.CharField(
        label='Facção', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cliente = forms.CharField(
        label='Cliente', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    pedido = forms.CharField(
        label='Pedido Tussor', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    pedido_cliente = forms.CharField(
        label='Pedido de cliente', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def clean_faccao(self):
        faccao = self.cleaned_data['faccao'].upper()
        data = self.data.copy()
        data['faccao'] = faccao
        self.data = data
        return faccao

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].upper()
        data = self.data.copy()
        data['cliente'] = cliente
        self.data = data
        return cliente

from django import forms


class InfAdProdForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class RemessaIndustrForm(forms.Form):
    data_de = forms.DateField(
        label='Data inicial', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='Data final', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    faccao = forms.CharField(
        label='Facção', required=False,
        help_text='Busca no nome e no CNPJ da facção',
        widget=forms.TextInput(attrs={'type': 'string'}))

    cliente = forms.CharField(
        label='Cliente', required=False,
        help_text='Busca no nome e no CNPJ do cliente',
        widget=forms.TextInput(attrs={'type': 'string'}))

    pedido = forms.CharField(
        label='Pedido Tussor', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    pedido_cliente = forms.CharField(
        label='Pedido de cliente', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('T', 'Todas as remessas'),
               ('S', 'Só remessas Sem retorno'),
               ('C', 'Só remessas Com retorno'),
               ]
    retorno = forms.ChoiceField(
        label='Retorno', choices=CHOICES, initial='T')

    CHOICES = [('C', 'Apenas por cor'),
               ('T', 'Por cor e tamanho'),
               ]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='C')

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

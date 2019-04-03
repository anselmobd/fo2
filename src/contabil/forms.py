from django import forms


class InfAdProdForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class RemessaIndustrBaseForm(forms.Form):
    data_de = forms.DateField(
        label='NF Remessa - Data inicial', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='NF Remessa - Data final', required=False,
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

    op = forms.CharField(
        label='OP', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [('T', 'Todas as remessas'),
               ('S', 'Só remessas Sem retorno'),
               ('C', 'Só remessas Com retorno'),
               ]
    retorno = forms.ChoiceField(
        label='Retorno', choices=CHOICES, initial='T')

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


class RemessaIndustrNFForm(RemessaIndustrBaseForm):
    CHOICES = [('T', 'Todas as remessas'),
               ('A', 'Ativa'),
               ('C', 'Canceladas'),
               ('D', 'Devolvidas'),
               ]
    situacao = forms.ChoiceField(
        label='Situação', choices=CHOICES, initial='A')

    data_ret_de = forms.DateField(
        label='NF Retorno - Data inicial', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ret_ate = forms.DateField(
        label='NF Retorno - Data final', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    nf_ret = forms.CharField(
        label='NF Retorno', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    nf = forms.CharField(
        label='NF Remessa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [('I', 'Por item de NF de remessa'),
               ('N', 'Por NF de remessa'),
               ]
    detalhe = forms.ChoiceField(
        label='Detalhamento', choices=CHOICES, initial='N')


class RemessaIndustrForm(RemessaIndustrNFForm):
    CHOICES = [('C', 'Apenas por cor'),
               ('T', 'Por cor e tamanho'),
               ]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='C')

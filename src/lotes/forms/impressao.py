from pprint import pprint

from django import forms

from produto.models import ProdutoItem


class ImprimeCaixaLotesForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    ultimo = forms.CharField(
        label='Lote em última etiqueta de caixa impressa', required=False,
        max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number'}))
    ultima_cx = forms.CharField(
        label='Número da última caixa impressa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    pula = forms.IntegerField(
        label='Pula quantos pacotes', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    qtd_lotes = forms.IntegerField(
        label='Imprime quantos pacotes', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    CHOICES = [
        (
            'etiqueta-de-caixa-com-barras-de-n-lotes',
            'Etiqueta de caixa com barras de N lotes',
        ),
        (
            'etiqueta-de-caixa-de-lotes',
            'Etiqueta de caixa de lotes',
        )
    ]
    impresso = forms.ChoiceField(
        label='Impresso', choices=CHOICES, initial='B')
    obs1 = forms.CharField(
        label='Observação 1', required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'style': 'width:20en'}))
    obs2 = forms.CharField(
        label='Observação 2', required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'style': 'width:20en'}))

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class ImprimeLotesForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    estagio = forms.CharField(
        label='Estágio de quebra de lote', required=False,
        help_text='Só imprime cartela de lote com quantidade parcial nesse '
                  'estágio.',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    order = forms.ChoiceField(
        label='Ordem',
        choices=[('t',  'Tamanho/Cor/OC'), ('o', 'OC'),
                 ('c', 'Cor/Tamanho/OC')])
    pula = forms.IntegerField(
        label='Pula quantos lotes', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    qtd_lotes = forms.IntegerField(
        label='Imprime quantos lotes', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    oc_inicial = forms.IntegerField(
        label='OC inicial', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    oc_final = forms.IntegerField(
        label='OC final', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    ultimo = forms.CharField(
        label='Último lote impresso', required=False,
        max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number'}))
    CHOICES = [('A', 'Etiqueta adesiva'),
               ('C', 'Cartela'),
               ('F', 'Cartela de fundo')]
    impresso = forms.ChoiceField(
        label='Impresso', choices=CHOICES, initial='A')
    obs1 = forms.CharField(
        label='Observação 1', required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'style': 'width:20em'}))
    obs2 = forms.CharField(
        label='Observação 2', required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'style': 'width:30em'}))

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class ImprimeOb1Form(forms.Form):
    os = forms.IntegerField(
        label='OS',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    caixa_inicial = forms.IntegerField(
        label='Caixa inicial', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    caixa_final = forms.IntegerField(
        label='Caixa final', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))


class ImprimeTagForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=ProdutoItem.objects.all())
    quant = forms.IntegerField(
        label='Quantidade',
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_quant(self):
        quant = self.cleaned_data['quant']
        if quant < 1:
            raise forms.ValidationError(
                "Informe uma quantidade maior que zero.")
        return quant

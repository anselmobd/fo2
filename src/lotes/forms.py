from django import forms

from produto.models import Colecao


class LoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class OpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class OsForm(forms.Form):
    os = forms.CharField(
        label='OS',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class AnPeriodoAlterForm(forms.Form):
    periodo_de = forms.CharField(
        label='Período: De',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    periodo_ate = forms.CharField(
        label='Até', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    alternativa = forms.CharField(
        label='Alternativa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_periodo(self, periodo):
        try:
            i_periodo = int(float(periodo))
            if i_periodo < 0:
                periodo = None
        except ValueError:
            periodo = None
        return periodo

    def clean_periodo_de(self):
        return self.clean_periodo(self.cleaned_data['periodo_de'])

    def clean_periodo_ate(self):
        return self.clean_periodo(self.cleaned_data['periodo_ate'])


class AnDtCorteAlterForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De',
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    alternativa = forms.CharField(
        label='Alternativa', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    # roteiro = forms.CharField(
    #     label='Roteiro', required=False,
    #     widget=forms.TextInput(attrs={'type': 'number'}))

    # tipo = forms.CharField(
    #     label='Tipo (MD, PG, PA)', required=False, widget=forms.TextInput)

    # def clean_tipo(self):
    #     tipo = self.cleaned_data['tipo'].upper()
    #     if tipo not in ('MD', 'PG', 'PA'):
    #         tipo = ''
    #     return tipo


class ResponsPorEstagioForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    usuario = forms.CharField(
        label='Usuário', max_length=20, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    CHOICES = [('e', 'Por estágio'),
               ('u', 'Por usuário')]
    ordem = forms.ChoiceField(
        choices=CHOICES, initial='e', widget=forms.RadioSelect())

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario'].upper()
        data = self.data.copy()
        data['usuario'] = usuario
        self.data = data
        return usuario


class ImprimeLotesForm(forms.Form):
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


class ImprimePacote3LotesForm(forms.Form):
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
    CHOICES = [('B', 'Etiqueta de caixa com barras de 3 lotes'),
               ('C', 'Etiqueta de caixa de lotes')]
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


class OpPendenteForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    periodo_de = forms.CharField(
        label='Período: De', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    periodo_ate = forms.CharField(
        label='Até', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    colecao = forms.ModelChoiceField(
        label='Coleção', required=False,
        queryset=Colecao.objects.exclude(colecao=0).order_by(
            'colecao'), empty_label="(Todas)")

    CHOICES = [('-', 'Ambas (2 e 4)'),
               ('2', '2 - Ordem cofecção gerada'),
               ('4', '4 - Ordens em produção')]
    situacao = forms.ChoiceField(
        label='Situação', choices=CHOICES, initial='0')

    def clean_periodo(self, periodo, default):
        try:
            i_periodo = int(float(periodo))
            if i_periodo < 0:
                periodo = default
        except ValueError:
            periodo = default
        return periodo

    def clean_periodo_de(self):
        return self.clean_periodo(self.cleaned_data['periodo_de'], 0)

    def clean_periodo_ate(self):
        return self.clean_periodo(self.cleaned_data['periodo_ate'], 9999)

    def clean_situacao(self):
        if self.cleaned_data['situacao'] == '-':
            return ''
        else:
            return self.cleaned_data['situacao']


class PedidoForm(forms.Form):
    pedido = forms.CharField(
        label='Pedido',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class ModeloTermicaForm(forms.ModelForm):
    gabarito = forms.CharField(
        label='Gabarito',
        widget=forms.Textarea(
            attrs={'max_length': 8192, 'rows': 20, 'cols': 79}))


class DistribuicaoForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    data_de = forms.DateField(
        label='Data da distribuição: De',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_estagio(self):
        estagio = self.cleaned_data['estagio']
        if estagio == '':
            estagio = '22'
        data = self.data.copy()
        data['estagio'] = estagio
        self.data = data
        return estagio


class BuscaOpForm(forms.Form):
    ref = forms.CharField(
        label='Referência', required=False, min_length=5, max_length=5,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class ExpedicaoForm(forms.Form):
    embarque_de = forms.DateField(
        label='Data do embarque: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    embarque_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    pedido_tussor = forms.CharField(
        label='Pedido na Tussor', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    pedido_cliente = forms.CharField(
        label='Pedido no cliente', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    cliente = forms.CharField(
        label='Cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('r', 'Por referência'),
               ('c', 'Por referência-cor-tamanho')]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='r')

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].upper()
        data = self.data.copy()
        data['cliente'] = cliente
        self.data = data
        return cliente

    def clean(self):
        clean_ef = super(ExpedicaoForm, self).clean()

        if not any(
            clean_ef.get(x, '')
            for x in (
                'embarque_de',
                'embarque_ate',
                'pedido_tussor',
                'pedido_cliente',
                'cliente',
            )
        ):
            list_msg = ['Ao menos um destes campos deve ser preenchido']
            self._errors['embarque_de'] = self.error_class(list_msg)
            self._errors['embarque_ate'] = self.error_class(list_msg)
            self._errors['pedido_tussor'] = self.error_class(list_msg)
            self._errors['pedido_cliente'] = self.error_class(list_msg)
            self._errors['cliente'] = self.error_class(list_msg)

        return clean_ef

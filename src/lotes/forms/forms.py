from datetime import datetime, timedelta

from django import forms

from produto.models import ProdutoItem
from systextil.models import Colecao, Familia


class LoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote/OC', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class OpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

class HistoricoOpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    oc = forms.CharField(
        label='OC', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    dia = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    usuario = forms.CharField(
        label='Usuário', max_length=20, required=False,
        widget=forms.TextInput(attrs={
            'type': 'string',
            'style': 'text-transform:uppercase;',
        }))
    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())


class OsForm(forms.Form):
    os = forms.CharField(
        label='OS',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class PeriodoAlterForm(forms.Form):
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


class DtCorteAlterForm(forms.Form):
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
               ('2', '2 - Ordem confecção gerada'),
               ('4', '4 - Ordens em produção')]
    situacao = forms.ChoiceField(
        label='Situação', choices=CHOICES, initial='0')

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        label='Tipo de produto', choices=CHOICES, initial='t')

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


class ModeloTermicaForm(forms.ModelForm):
    gabarito = forms.CharField(
        label='Gabarito',
        widget=forms.Textarea(
            attrs={'max_length': 8192, 'rows': 20, 'cols': 79}))


class DistribuicaoForm(forms.Form):
    # estagio = forms.CharField(
    #     label='Estágio', max_length=2, required=False,
    #     widget=forms.TextInput(attrs={'type': 'number',
    #                            'autofocus': 'autofocus'}))
    data_de = forms.DateField(
        label='Data da distribuição: De',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    familia = forms.ModelChoiceField(
        label='Família (tear)', required=False,
        queryset=Familia.objects.filter(
            divisao_producao__range=['3000', '3999']).order_by(
            'divisao_producao'), empty_label="(Todas)")

    # def clean_estagio(self):
    #     estagio = self.cleaned_data['estagio']
    #     if estagio == '':
    #         estagio = '22'
    #     data = self.data.copy()
    #     data['estagio'] = estagio
    #     self.data = data
    #     return estagio


class BuscaOpForm(forms.Form):
    ref = forms.CharField(
        label='Referência', required=False, min_length=1, max_length=5,
        help_text='(aceita filtro com "%")',
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))
    modelo = forms.CharField(
        label='Modelo', max_length=4, min_length=1, required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    deposito = forms.CharField(
        label='Depósito', required=False, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        label='Tipo de produto', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas'),
               ('p', 'Alternativa de produção'),
               ('e', 'Alternativa de expedição'),
               ]
    tipo_alt = forms.ChoiceField(
        label='Tipo de alternativa', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('a', 'Ativas'),
               ('c', 'Canceladas'),
               ]
    situacao = forms.ChoiceField(
        label='Situação da OP', choices=CHOICES, initial='a')

    CHOICES = [('t', 'Todas as OPs'),
               ('p', 'Em produção'),
               ('f', 'Finalizadas'),
               ('p63', 'Em produção, exceto OPs apenas no 63-CD'),
               ('f63', 'Finalizadas, incluindo OPs apenas no 63-CD'),
               ]
    posicao = forms.ChoiceField(
        label='Posição da produção', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('e', 'OP de estoque'),
               ('p', 'OP de pedido (qualquer)'),
               ('n', 'OP de pedido não faturado'),
               ('f', 'OP de pedido faturado'),
               ('c', 'OP de pedido faturado e cancelado'),
               ('d', 'OP de pedido faturado e devolvido'),
               ('a', 'OP de pedido faturável '
                     '(não faturado ou faturado e cancelado)'),
               ('i', 'OP de pedido não faturável '
                     '(faturado ou faturado e devolvido)'),
               ]
    motivo = forms.ChoiceField(
        label='Motivo da OP', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('z', 'Zerada'),
               ('n', 'Não zerada'),
               ]
    quant_fin = forms.ChoiceField(
        label='Quantidade finalizada', choices=CHOICES, initial='t')

    CHOICES = [('t', 'Todas as OPs'),
               ('z', 'Zerada'),
               ('n', 'Não zerada'),
               ]
    quant_emp = forms.ChoiceField(
        label='Quantidade em produção', choices=CHOICES, initial='t')

    data_de = forms.DateField(
        label='Data do Corte: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    apenas_totais = forms.BooleanField(
        label='Apenas totais', required=False,
        widget=forms.CheckboxInput(attrs={'checked': False}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

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


class BuscaPedidoForm(forms.Form):
    modelo = forms.CharField(
        label='Modelo', max_length=5, min_length=1,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

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

class ExpedicaoForm(forms.Form):
    embarque_de = forms.DateField(
        label='Data do embarque: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))

    embarque_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    emissao_de = forms.DateField(
        label='Data da emissão: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    emissao_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    pedido_tussor = forms.CharField(
        label='Pedido na Tussor', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    pedido_cliente = forms.CharField(
        label='Pedido no cliente', required=False)

    cliente = forms.CharField(
        label='Cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('-', 'Todos os Depósitos'),
               ('101', '101-PA Atacado'),
               ('102', '102-PA Varejo')]
    deposito = forms.ChoiceField(
        label='Depósito', choices=CHOICES, initial='-')

    CHOICES = [
        ('r', 'Por pedido-referência'),
        ('c', 'Por pedido-referência-cor-tamanho'),
        ('p', 'Por pedido (e qualidade de GTIN)'),
        ('g', 'Por grade de referência'),
    ]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='p')

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

    CHOICES = [('r', 'Por referência'),
               ('c', 'Por referência-cor-tamanho')]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='c')

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
            data_ate = self.cleaned_data['data_de']
            data_ate = data_ate.replace(
                month=data_ate.month % 12 + 1)-timedelta(days=1)
            data = self.data.copy()
            data['data_ate'] = data_ate
            self.data = data
        return data_ate


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


class TotaisEstagioForm(forms.Form):
    CHOICES = [('p', 'De produção'),
               ('e', 'De expedição'),
               ('t', 'Todos'),
               ]
    tipo_roteiro = forms.ChoiceField(
        label='Tipo de roteiro de OP',
        choices=CHOICES, required=False, initial='p')

    cliente = forms.CharField(
        label='Produtos do cliente', required=False,
        help_text='Parte do nome ou início do CNPJ.',
        widget=forms.TextInput(attrs={'type': 'string'}))

    deposito = forms.CharField(
        label='Depósito', required=False, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].upper()
        data = self.data.copy()
        data['cliente'] = cliente
        self.data = data
        return cliente


class QuantEstagioForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    ref = forms.CharField(
        label='Referência', required=False, min_length=1, max_length=5,
        help_text='(aceita filtro com "%")',
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        choices=CHOICES, required=False, initial='t')

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class LeadColecaoForm(forms.Form):
    lead = forms.IntegerField(
        required=False, min_value=0, max_value=100,
        widget=forms.TextInput(attrs={'type': 'number'}))


class LoteMinColecaoForm(forms.Form):
    lm_tam = forms.IntegerField(
        label='Lote mínimo por tamanho',
        required=False, min_value=0, max_value=10000,
        widget=forms.TextInput(attrs={'type': 'number'}))

    lm_cor = forms.IntegerField(
        label='Lote mínimo por cor',
        required=False, min_value=0, max_value=10000,
        widget=forms.TextInput(attrs={'type': 'number'}))


class RegrasLoteMinTamanhoForm(forms.Form):
    min_para_lm = forms.IntegerField(
        label='% mínimo para aplicação do lote mínimo por tamanho',
        required=False, min_value=0, max_value=100,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    lm_cor_sozinha = forms.ChoiceField(
        label='Aplica lote mínimo por cor quando único tamanho',
        choices=CHOICES, required=False, initial='s')


class RegrasLoteCaixaForm(forms.Form):
    lotes_caixa = forms.IntegerField(
        label='Lotes por caixa',
        min_value=0, max_value=10,
        widget=forms.TextInput(attrs={'type': 'number'}))


class AddRegrasLoteCaixaForm(forms.Form):
    colecao = forms.ModelChoiceField(
        label='Coleção', required=True,
        queryset=Colecao.objects.exclude(colecao=0).order_by('colecao'))

    referencia = forms.CharField(
        label='Referência', required=False, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={
            'type': 'string',
            'style': 'text-transform:uppercase;',
        }))

    lotes_caixa = forms.IntegerField(
        label='Lotes por caixa',
        min_value=0, max_value=10,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_referencia(self):
        referencia = self.cleaned_data['referencia'].upper()
        data = self.data.copy()
        data['referencia'] = referencia
        self.data = data
        return referencia


class ProduzirModeloGradeForm(forms.Form):
    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    deposito = forms.ChoiceField(
        label='Considera depósito',
        choices=CHOICES, required=False, initial='s')


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

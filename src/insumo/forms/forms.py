from pprint import pprint

from django import forms
from django.utils import timezone

from base.forms.custom import O2BaseForm
from base.forms.fields import (
    O2FieldCorForm,
    O2FieldFiltroForm,
    O2FieldNivelForm,
    O2FieldRefForm,
    O2FieldTamanhoForm,
)

from systextil.models import (
    Colecao,
    ContaEstoque,
    Periodo,
    TipoContaEstoque,
) 


class FiltroMpForm(
        O2BaseForm,
        O2FieldFiltroForm):

    conta_estoque = forms.ModelChoiceField(
        label='Conta de estoque do insumo', required=False,
        queryset=ContaEstoque.objects.exclude(conta_estoque=0).order_by(
            'conta_estoque'),
        empty_label="(Todas)")

    # CHOICES = [(None, '--Todos--')]
    # tipos_ce = TipoContaEstoque.objects.all()
    # for tipo_ce in tipos_ce:
    #     CHOICES.append((
    #         tipo_ce.codigo,
    #         '{}-{}'.format(tipo_ce.codigo, tipo_ce.descricao)
    #     ))

    tipo_conta_estoque = forms.ChoiceField(
        label='Tipo de conta de estoque do insumo',
        required=False, initial=None)

    def __init__(self, *args, **kwargs):
        super(FiltroMpForm, self).__init__(*args, **kwargs)

        CHOICES = [(None, '--Todos--')]
        tipos_ce = TipoContaEstoque.objects.all()
        for tipo_ce in tipos_ce:
            CHOICES.append((
                tipo_ce.codigo,
                '{}-{}'.format(tipo_ce.codigo, tipo_ce.descricao)
            ))

        self.fields['tipo_conta_estoque'].choices = CHOICES

    class Meta:
        autofocus_field = 'filtro'


class RefForm(forms.Form):
    item = forms.CharField(
        label='Referência', max_length=7, min_length=5,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_item(self):
        item = self.cleaned_data['item'].upper()
        data = self.data.copy()
        data['item'] = item
        self.data = data
        return item


class RolosBipadosForm(forms.Form):
    dispositivo = forms.CharField(
        label='Dispositivo ou Usuário', max_length=32, required=False,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    ref = forms.CharField(
        label='Referência', max_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', max_length=6, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    data_de = forms.DateField(
        label='Data de bipagem: De', required=False,
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class BipaRoloForm(forms.Form):
    rolo = forms.CharField(
        label='Rolo', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    identificado = forms.CharField(
        label='identificado', required=False,
        widget=forms.HiddenInput())


class NecessidadeForm(forms.Form):
    op = forms.CharField(
        label='OP', required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    data_corte = forms.DateField(
        label='Data do Corte', required=False,
        help_text='(Se informar "Data final do Corte",'
                  ' a "Data do Corte" funciona como inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_corte_ate = forms.DateField(
        label='Data final do Corte', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    periodo_corte = forms.CharField(
        label='Período do Corte', required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    data_compra = forms.DateField(
        label='Data de "Compra"', required=False,
        help_text='(Se informar "Data final de Compra",'
                  ' a "Data de Compra" funciona como inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_compra_ate = forms.DateField(
        label='Data final de "Compra"', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    periodo_compra = forms.CharField(
        label='Período de "Compra"', required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    insumo = forms.CharField(
        label='Referência do insumo',
        max_length=5, min_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    conta_estoque = forms.ModelChoiceField(
        label='Conta de estoque do insumo', required=False,
        queryset=ContaEstoque.objects.exclude(conta_estoque=0).order_by(
            'conta_estoque'), empty_label="(Todas)")

    ref = forms.CharField(
        label='Referência produzida',
        max_length=5, min_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    conta_estoque_ref = forms.ModelChoiceField(
        label='Conta de estoque do produzido', required=False,
        queryset=ContaEstoque.objects.exclude(conta_estoque=0).order_by(
            'conta_estoque'), empty_label="(Todas)")

    colecao = forms.ModelChoiceField(
        label='Coleção do produzido', required=False,
        queryset=Colecao.objects.exclude(colecao=0).order_by(
            'colecao'), empty_label="(Todas)")

    CHOICES = [('t', 'Todos os insumos das OPs'),
               ('a', 'Apenas insumos de estágios não avançados dos lotes'),
               ('d', 'Apenas insumos de estágios não avançados e em estágios '
                     'com depósito')]
    quais = forms.ChoiceField(
        label='Quais insumos', choices=CHOICES, initial='d')

    def clean_insumo(self):
        insumo = self.cleaned_data['insumo'].upper()
        data = self.data.copy()
        data['insumo'] = insumo
        self.data = data
        return insumo

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_periodo(self, periodo):
        try:
            i_periodo = int(float(periodo))
            if i_periodo < 0:
                i_periodo = None
        except ValueError:
            i_periodo = None
        return i_periodo

    def clean_periodo_corte(self):
        return self.clean_periodo(self.cleaned_data['periodo_corte'])

    def clean_periodo_compra(self):
        return self.clean_periodo(self.cleaned_data['periodo_compra'])


class MapaComprasNecessidadesForm(
        O2BaseForm,
        O2FieldNivelForm,
        O2FieldRefForm,
        O2FieldTamanhoForm,
        O2FieldCorForm):

    CHOICES = [
        ('m', 'Como no mapa de compras'),
        ('t', 'Todas as colunas'),
    ]
    colunas = forms.ChoiceField(choices=CHOICES)

    class Meta:
        order_fields = [
            'nivel',
            'ref',
            'tamanho',
            'cor',
            'colunas',
        ]
        required_fields = [
            'nivel',
            'ref',
            'tamanho',
            'cor',
        ]
        autofocus_field = 'nivel'
        initial_values = {
            'nivel': 9,
            'colunas': 'm',
        }


class ReceberForm(forms.Form):
    insumo = forms.CharField(
        label='Referência do insumo',
        max_length=5, min_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    conta_estoque = forms.ModelChoiceField(
        label='Conta de estoque do insumo', required=False,
        queryset=ContaEstoque.objects.exclude(conta_estoque=0).order_by(
            'conta_estoque'), empty_label="(Todas)")

    CHOICES = [('a', 'Apenas insumos com quantidades a receber'),
               ('t', 'Todos os insumos com pedidos')]
    recebimento = forms.ChoiceField(
        label='Recebimento',
        choices=CHOICES, initial='a', widget=forms.RadioSelect())

    def clean_insumo(self):
        insumo = self.cleaned_data['insumo'].upper()
        data = self.data.copy()
        data['insumo'] = insumo
        self.data = data
        return insumo


class EstoqueForm(forms.Form):
    insumo = forms.CharField(
        label='Referência do insumo',
        max_length=5, min_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    conta_estoque = forms.ModelChoiceField(
        label='Conta de estoque do insumo', required=False,
        queryset=ContaEstoque.objects.exclude(conta_estoque=0).order_by(
            'conta_estoque'), empty_label="(Todas)")

    def clean_insumo(self):
        insumo = self.cleaned_data['insumo'].upper()
        data = self.data.copy()
        data['insumo'] = insumo
        self.data = data
        return insumo


class MapaRefsForm(forms.Form):
    insumo = forms.CharField(
        label='Referência do insumo',
        help_text='(código inteiro ou parcial)',
        max_length=5, min_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    conta_estoque = forms.ModelChoiceField(
        label='Conta de estoque do insumo', required=False,
        queryset=ContaEstoque.objects.exclude(conta_estoque=0).order_by(
            'conta_estoque'), empty_label="(Todas)")

    # CHOICES = [('a', 'Apenas insumos com necessidades a partir desta semana'),
    #            ('t', 'Todos os insumos')]
    # necessidade = forms.ChoiceField(
    #     label='Necessidades',
    #     help_text='(data de necessidade = data do corte - 7 dias)',
    #     choices=CHOICES, initial='a', widget=forms.RadioSelect())

    def clean_insumo(self):
        insumo = self.cleaned_data['insumo'].upper()
        data = self.data.copy()
        data['insumo'] = insumo
        self.data = data
        return insumo


class PrevisaoForm(forms.Form):
    periodo = forms.CharField(
        label='Período da previsão', max_length=4, min_length=1,
        help_text='(Início da descrição da previsão)',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    def clean_periodo(self):
        try:
            periodo = int(float(self.cleaned_data['periodo']))
            if periodo < 0:
                periodo = None
        except ValueError:
            periodo = None
        return periodo


class MapaPorSemanaForm(forms.Form):
    periodo = forms.CharField(
        label='Período (semana)', max_length=4, min_length=1,
        help_text='(segunda-feira inicial)',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    qtd_semanas = forms.CharField(
        label='Quantidade de semanas', max_length=2, min_length=1,
        widget=forms.TextInput(attrs={'type': 'number'}))

    qtd_itens = forms.CharField(
        label='Quantidade limite de itens processados abaixo',
        max_length=4, min_length=1, required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [(2, 'Nível 2 - em rolos'),
               (9, 'Nível 9 - demais insumos'),
               (0, 'Ambos')]
    nivel = forms.ChoiceField(label='Nível', choices=CHOICES, initial=0)

    CHOICES = [('U', 'Utilizados em alguma estrutura de produto'),
               ('N', 'Não utilizados em nenhum estrutura de produto'),
               ('T', 'Todos')]
    uso = forms.ChoiceField(choices=CHOICES, initial='U')

    insumo = forms.CharField(
        label='Filtro do insumo',
        help_text='(código exato ou parciais do código e descrição)',
        min_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def __init__(self, *args, **kwargs):
        super(MapaPorSemanaForm, self).__init__(*args, **kwargs)

        periodo_atual = Periodo.confeccao.filter(
            data_ini_periodo__lte=timezone.now()
        ).filter(
            data_fim_periodo__gte=timezone.now()
        ).values()
        periodo_default = periodo_atual[0]['periodo_producao'] \
            if periodo_atual else ''

        self.fields['periodo'].initial = periodo_default
        self.fields['qtd_semanas'].initial = 1
        self.fields['qtd_itens'].initial = 30

    def clean__positive(self, field_name):
        try:
            field_value = int(float(self.cleaned_data[field_name]))
            if field_value <= 0:
                field_value = None
        except ValueError:
            field_value = None
        if field_value is None:
            raise forms.ValidationError(
                "Esperado um valor numérico maior que zero.",
                code='não positivo')
        return field_value

    def clean_periodo(self):
        return self.clean__positive('periodo')

    def clean_qtd_semanas(self):
        return self.clean__positive('qtd_semanas')

    def clean_qtd_itens(self):
        if self.cleaned_data['qtd_itens'].zfill(1) == '0':
            return '0'
        return self.clean__positive('qtd_itens')


class MapaComprasSemanaForm(forms.Form):
    periodo = forms.CharField(
        label='Período (semana)', max_length=4, min_length=1,
        help_text='(segunda-feira inicial)',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    qtd_semanas = forms.CharField(
        label='Quantidade de semanas', max_length=2, min_length=1, initial=3,
        widget=forms.TextInput(attrs={'type': 'number'}))

    qtd_itens = forms.CharField(
        label='Quantidade limite de itens processados abaixo',
        max_length=4, min_length=1, required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    CHOICES = [(2, 'Nível 2 - em rolos'),
               (9, 'Nível 9 - demais insumos'),
               (0, 'Ambos (níveis 2 e 9)')]
    nivel = forms.ChoiceField(label='Nível', choices=CHOICES, initial=0)

    CHOICES = [('U', 'Insumos utilizados em alguma estrutura de produto'),
               ('T', 'Todos'),
               ('N', 'Insumos não utilizados em nenhum estrutura de produto')]
    uso = forms.ChoiceField(choices=CHOICES, initial='U')

    insumo = forms.CharField(
        label='Filtro do insumo',
        help_text='(código exato ou parciais do código e descrição)',
        min_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    # CHOICES = [('A', 'Antiga'),
    #            ('N', 'Nova')]
    # versao = forms.ChoiceField(label='Versão', choices=CHOICES, initial='U')
    versao = forms.CharField(initial='N', widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(MapaComprasSemanaForm, self).__init__(*args, **kwargs)

        periodo_atual = Periodo.confeccao.filter(
            data_ini_periodo__lte=timezone.now()
        ).filter(
            data_fim_periodo__gte=timezone.now()
        ).values()
        periodo_default = periodo_atual[0]['periodo_producao'] \
            if periodo_atual else ''

        self.fields['periodo'].initial = periodo_default
        # self.fields['qtd_itens'].initial = 30

    def clean__positive(self, field_name):
        try:
            field_value = int(float(self.cleaned_data[field_name]))
            if field_value <= 0:
                field_value = None
        except ValueError:
            field_value = None
        if field_value is None:
            raise forms.ValidationError(
                "Esperado um valor numérico maior que zero.",
                code='não positivo')
        return field_value

    def clean_periodo(self):
        return self.clean__positive('periodo')

    def clean_qtd_semanas(self):
        return self.clean__positive('qtd_semanas')

    def clean_qtd_itens(self):
        if self.cleaned_data['qtd_itens'].zfill(1) == '0':
            return '0'
        return self.clean__positive('qtd_itens')


class MapaSemanalForm(forms.Form):
    periodo = forms.CharField(
        label='Período (semana)', max_length=4, min_length=1,
        help_text='(segunda-feira inicial)',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    CHOICES = [(2, 'Nível 2 - em rolos'),
               (9, 'Nível 9 - demais insumos'),
               (0, 'Ambos')]
    nivel = forms.ChoiceField(label='Nível', choices=CHOICES, initial=0)

    CHOICES = [('U', 'Utilizados em alguma estrutura de produto'),
               ('N', 'Não utilizados em nenhum estrutura de produto'),
               ('T', 'Todos')]
    uso = forms.ChoiceField(choices=CHOICES, initial='U')

    insumo = forms.CharField(
        label='Filtro do insumo',
        help_text='(código exato ou parciais do código e descrição)',
        min_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def __init__(self, *args, **kwargs):
        super(MapaSemanalForm, self).__init__(*args, **kwargs)

        periodo_atual = Periodo.confeccao.filter(
            data_ini_periodo__lte=timezone.now()
        ).filter(
            data_fim_periodo__gte=timezone.now()
        ).values()
        periodo_default = periodo_atual[0]['periodo_producao'] \
            if periodo_atual else ''

        self.fields['periodo'].initial = periodo_default

    def clean__positive(self, field_name):
        try:
            field_value = int(float(self.cleaned_data[field_name]))
            if field_value <= 0:
                field_value = None
        except ValueError:
            field_value = None
        if field_value is None:
            raise forms.ValidationError(
                "Esperado um valor numérico maior que zero.",
                code='não positivo')
        return field_value

    def clean_periodo(self):
        return self.clean__positive('periodo')

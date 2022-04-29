from pprint import pprint

from django import forms

from base.forms.custom import O2BaseForm
from base.forms.fields import (
    O2FieldCorForm,
    O2FieldModeloForm,
    O2FieldRefForm,
)

from systextil.models.base import Empresa


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

    CHOICES = [('I', 'Por item de NF de remessa'),
               ('1', 'Por item de nível 1 de NF de remessa'),
               ('R', 'Por referência de nível 1 de NF de remessa'),
               ('N', 'Por NF de remessa'),
               ]
    detalhe = forms.ChoiceField(
        label='Detalhamento', choices=CHOICES, initial='N')


class RemessaIndustrForm(RemessaIndustrBaseForm):
    CHOICES = [('C', 'Apenas por cor'),
               ('T', 'Por cor e tamanho'),
               ]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='C')


class NotaFiscalForm(forms.Form):
    empresa = forms.ChoiceField(
        required=True, initial=None)
    nf = forms.CharField(
        label='Nota fiscal',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super(NotaFiscalForm, self).__init__(*args, **kwargs)

        CHOICES = []
        empresas = Empresa.objects.all().order_by('codigo_empresa')
        for empresa in empresas:
            CHOICES.append((
                empresa.codigo_empresa,
                f"{empresa.codigo_empresa}-{empresa.nome_fantasia}",
            ))
        self.fields['empresa'].choices = CHOICES


class buscaNFForm(
        O2BaseForm,
        O2FieldCorForm,
        O2FieldModeloForm,
        O2FieldRefForm,
        ):

    pagina = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    class Meta:
        autofocus_field = 'ref'
        order_fields = [
            'ref',
            'modelo',
            'cor',
        ]

    def clean(self):
        filtros = (
            self.cleaned_data['ref'] +
            self.cleaned_data['cor']
        )
        if len(filtros.strip()) == 0 and self.cleaned_data['modelo'] is None:
            raise forms.ValidationError(
                "Algum filtro deve ser definido.")


class UploadArquivoForm(forms.Form):
    arquivo = forms.FileField()

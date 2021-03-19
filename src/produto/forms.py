import re

from django import forms

from base.forms import \
    O2BaseForm, \
    O2FieldNivelForm, \
    O2FieldRefForm, \
    O2FieldTamanhoForm, \
    O2FieldCorForm, \
    O2FieldGtinForm, \
    O2FieldFiltroForm

from systextil.models import Produto as S_Produto

from .models import Produto


class ModeloForm(forms.Form):
    modelo = forms.CharField(
        label='Modelo', max_length=4, min_length=1,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class FiltroRefForm(
        O2BaseForm,
        O2FieldFiltroForm,
        O2FieldCorForm):

    alternativa = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    roteiro = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    class Meta:
        order_fields = ['filtro', 'cor', 'alternativa', 'roteiro']
        autofocus_field = 'filtro'


class GtinPesquisaForm(
        O2BaseForm,
        O2FieldRefForm,
        O2FieldGtinForm):

    class Meta:
        order_fields = ['ref', 'gtin']
        autofocus_field = 'ref'


class GtinDefineForm(
        O2BaseForm,
        O2FieldRefForm,
        O2FieldTamanhoForm,
        O2FieldCorForm):

    class Meta:
        order_fields = ['ref', 'tamanho', 'cor']
        required_fields = ['ref']
        autofocus_field = 'ref'


class GtinDefineBarrasForm(
        O2BaseForm,
        O2FieldGtinForm):

    class Meta:
        autofocus_field = 'gtin'


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = '__all__'

    def clean(self):
        referencia = self.cleaned_data.get('referencia').upper()
        self.cleaned_data['referencia'] = referencia
        if len(referencia) != 5:
            raise forms.ValidationError(
                "Referência deve ter 5 números ou letras")
        if referencia >= 'A0000':
            raise forms.ValidationError("Referência não parece ser de PA")
        try:
            sprod = S_Produto.objects.get(
                nivel_estrutura='1', referencia=referencia)
        except S_Produto.DoesNotExist:
            raise forms.ValidationError("Referência não existe no Systêxtil")
        return self.cleaned_data


class GeraRoteirosRefForm(forms.Form):
    ref = forms.CharField(
        label='Referência', max_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class ClienteForm(forms.Form):
    cliente = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_cliente(self):
        cliente = self.cleaned_data['cliente'].upper()
        data = self.data.copy()
        data['cliente'] = cliente
        self.data = data
        return cliente


class ReferenciaForm(
        O2BaseForm,
        O2FieldRefForm):

    class Meta:
        required_fields = ['ref']
        autofocus_field = 'ref'


class ReferenciaNoneForm(
        O2BaseForm,
        O2FieldRefForm):

    class Meta:
        autofocus_field = 'ref'


class CustoDetalhadoForm(
        O2BaseForm,
        O2FieldNivelForm,
        O2FieldRefForm,
        O2FieldTamanhoForm,
        O2FieldCorForm):

    alternativa = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    class Meta:
        order_fields = [
            'nivel',
            'ref',
            'tamanho',
            'cor',
            'alternativa',
        ]
        required_fields = ['ref']
        autofocus_field = 'ref'
        initial_values = {
            'nivel': 1,
        }


class FiltroModeloForm(forms.Form):
    descricao = forms.CharField(
        label='Descrição', required=False,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_descricao(self):
        descricao = self.cleaned_data['descricao'].upper()
        data = self.data.copy()
        data['descricao'] = descricao
        self.data = data
        return descricao

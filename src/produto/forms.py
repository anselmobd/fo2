import re

from django import forms

from utils.forms import FiltroForm

from .models import Produto, S_Produto


class RefForm(forms.Form):
    ref = forms.CharField(
        label='Referência', max_length=5, min_length=5,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class ModeloForm(forms.Form):
    modelo = forms.CharField(
        label='Modelo', max_length=4, min_length=3,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class BuscaForm(FiltroForm):
    cor = forms.CharField(
        max_length=6, required=False,
        widget=forms.TextInput())

    alternativa = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    roteiro = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class GtinForm(forms.Form):
    ref = forms.CharField(
        label='Referência', max_length=5, min_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))
    gtin = forms.CharField(
        label='GTIN', max_length=13, min_length=13, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


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


class O2BaseForm(forms.Form):

    def saver(self, field_name, field):
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def cleanner_field(self, field):
        field = field.upper()
        field = re.search('[A-Z0-9]+', field).group(0)
        return field

    def cleanner(self, field_name):
        field = self.cleaned_data[field_name]
        if field != '':
            field = self.cleanner_field(field)
        return self.saver(field_name, field)

    def cleanner_pad_field(self, field, length):
        field = self.cleanner_field(field)
        field = field.lstrip('0')
        field = field.zfill(length)
        return field

    def cleanner_pad(self, field_name, length):
        field = self.cleaned_data[field_name]
        if field != '':
            field = self.cleanner_pad_field(field, length)
        return self.saver(field_name, field)


class O2FieldRefForm(forms.Form):
    ref = forms.CharField(
        label='Referência',
        required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def clean_ref(self):
        return O2BaseForm.cleanner_pad(self, 'ref', 5)


class O2FieldTamanhoForm(forms.Form):
    tamanho = forms.CharField(
        required=False,
        widget=forms.TextInput())

    def clean_tamanho(self):
        return O2BaseForm.cleanner(self, 'tamanho')


class O2FieldCorForm(forms.Form):
    cor = forms.CharField(
        required=False,
        widget=forms.TextInput())

    def clean_cor(self):
        return O2BaseForm.cleanner_pad(self, 'cor', 6)


class ReferenciaForm(
        O2BaseForm,
        O2FieldRefForm):
    pass


class CustoDetalhadoForm(
        O2BaseForm,
        O2FieldRefForm,
        O2FieldTamanhoForm,
        O2FieldCorForm):

    alternativa = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def __init__(self, *args, **kwargs):
        super(CustoDetalhadoForm, self).__init__(*args, **kwargs)
        self.order_fields([
            'ref',
            'tamanho',
            'cor',
            'alternativa',
        ])
        self.fields['ref'].required = True

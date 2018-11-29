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

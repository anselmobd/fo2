from django import forms

from produto.models import Colecao
from insumo.models import ContaEstoque


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
        label='Dispositivo', max_length=32, required=False,
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

    data_compra = forms.DateField(
        label='Data de "Compra"', required=False,
        help_text='(Se informar "Data final de Compra",'
                  ' a "Data de Compra" funciona como inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))

    data_compra_ate = forms.DateField(
        label='Data final de "Compra"', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

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

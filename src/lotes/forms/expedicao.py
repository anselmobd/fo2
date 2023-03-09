from pprint import pprint

from django import forms

from systextil.models import Colecao


__all__ = ['ExpedicaoForm']


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
        ('o', 'Por pedido (Obs., OP e Referência)'),
        ('g', 'Por grade de referência'),
    ]
    detalhe = forms.ChoiceField(
        label='Detalhe', choices=CHOICES, initial='p')

    CHOICES_CANC = [
        ('-', 'Todos'),
        ('C', 'Cancelado'),
        ('N', 'Não cancelado')
    ]
    cancelamento = forms.ChoiceField(
        choices=CHOICES_CANC, initial='N')

    CHOICES_FAT = [
        ('-', 'Todos'),
        ('F', 'Faturado'),
        ('N', 'Não faturado')
    ]
    faturamento = forms.ChoiceField(
        choices=CHOICES_FAT, initial='N')

    colecao = forms.ModelChoiceField(
        label='Coleção da referência', required=False,
        queryset=Colecao.objects.exclude(colecao=0).order_by(
            'colecao'), empty_label="(Todas)")

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
                'emissao_de',
                'emissao_ate',
                'pedido_tussor',
                'pedido_cliente',
                'cliente',
            )
        ):
            list_msg = ['Ao menos um destes campos deve ser preenchido']
            self._errors['embarque_de'] = self.error_class(list_msg)
            self._errors['embarque_ate'] = self.error_class(list_msg)
            self._errors['emissao_de'] = self.error_class(list_msg)
            self._errors['emissao_ate'] = self.error_class(list_msg)
            self._errors['pedido_tussor'] = self.error_class(list_msg)
            self._errors['pedido_cliente'] = self.error_class(list_msg)
            self._errors['cliente'] = self.error_class(list_msg)

        return clean_ef

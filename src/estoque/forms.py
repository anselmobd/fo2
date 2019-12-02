from django import forms
# from django.core.exceptions import ValidationError

from base.forms import O2BaseForm, O2FieldRefForm, O2FieldModeloForm
import geral


class PorDepositoForm(forms.Form):
    nivel = forms.IntegerField(
        label='Nível', required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    ref = forms.CharField(
        label='Referência ou modelo',
        required=True, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={'type': 'string'}))

    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cor = forms.CharField(
        label='Cor', required=False, max_length=6,
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [
        ('999', '--Todos--'),
        ('1001', '231, 101 e 102 - '
                 'MAT PRIMA + PA ATACADO E VAREJO 1ª QUALI.'),
    ]
    depositos = geral.queries.deposito()
    for deposito in depositos:
        if deposito['COD'] > 1:
            CHOICES.append((
                deposito['COD'],
                '{} - {}'.format(deposito['COD'], deposito['DESCR'])
            ))
    deposito = forms.ChoiceField(
        label='Depósito', choices=CHOICES, initial='999')

    CHOICES = [
        ('rct', 'Referência/Tamanho/Cor/Depósito'),
        ('r', 'Referência/Depósito'),
        ('tc', 'Tamanho/Cor'),
    ]
    agrupamento = forms.ChoiceField(
        choices=CHOICES, initial='rct')

    CHOICES = [('t', 'Todos'),
               ('a', 'PA'),
               ('g', 'PG'),
               ('b', 'PB'),
               ('p', 'PG/PB'),
               ('v', 'PA/PG/PB'),
               ('m', 'MD'),
               ]
    tipo = forms.ChoiceField(
        choices=CHOICES, initial='t')

    def upper_clean(self, field_name):
        field = self.cleaned_data[field_name].upper()
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def clean_ref(self):
        return self.upper_clean('ref')

    def clean_tam(self):
        return self.upper_clean('tam')

    def clean_cor(self):
        return self.upper_clean('cor')


# def validate_nivel_mp(value):
#     if value != 2 and value != 9:
#         raise ValidationError(
#             '%(value)s não é nível de MP',
#             params={'value': value},
#         )


class ValorForm(forms.Form):
    # nivel = forms.IntegerField(
    #     label='Nível', required=False,
    #     help_text='2=Tecidos/malhas, 9=Demais materiais',
    #     validators=[validate_nivel_mp],
    #     widget=forms.TextInput(attrs={'type': 'number',
    #                            'autofocus': 'autofocus'}))
    CHOICES = [
        ('2', '2 - Tecidos/malhas'),
        ('9', '9 - Demais materiais'),
    ]
    nivel = forms.ChoiceField(
        label='Nível',
        choices=CHOICES, initial='a')

    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    positivos = forms.ChoiceField(
        label='Quantidade positiva',
        choices=CHOICES, initial='s')

    zerados = forms.ChoiceField(
        label='Quantidade zerada',
        choices=CHOICES, initial='n')

    negativos = forms.ChoiceField(
        label='Quantidade negativa',
        choices=CHOICES, initial='n')

    preco_zerado = forms.ChoiceField(
        label='Preço zerado',
        choices=CHOICES, initial='n')

    CHOICES = [
        ('a', 'Apenas os depósitos indicados pelo Compras'),
        ('t', 'Todos os depósitos'),
    ]
    deposito_compras = forms.ChoiceField(
        label='Quanto aos depósitos',
        choices=CHOICES, initial='a')


class InventarioExpedicaoForm(forms.Form):
    data_ini = forms.DateField(
        label='Referências com movimento a partir da data:',
        widget=forms.DateInput(attrs={'type': 'date',
                               'autofocus': 'autofocus'}))


class ReferenciasEstoqueForm(
        O2BaseForm,
        O2FieldModeloForm):

    # CHOICES = [
    #     ('t', 'Todas'),
    #     ('m', 'Com movimentação'),
    #     ('e', 'Com estoque'),
    # ]
    # filtra_ref = forms.ChoiceField(
    #     label='Filtro de referências:',
    #     choices=CHOICES, initial='e')

    class Meta:
        order_fields = ['filtra_ref', 'modelo']
        autofocus_field = 'modelo'

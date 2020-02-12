from django import forms

from base.forms import O2BaseForm, O2FieldRefForm, O2FieldModeloForm


class ClienteForm(forms.Form):
    cnpj = forms.CharField(
        label='CNPJ (início) ou Razão Social (parte)',
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


class VendasPorForm(
        O2BaseForm,
        O2FieldRefForm):

    # cliente = forms.CharField(
    #     required=False,
    #     help_text='CNPJ (início) ou Razão Social (parte)',
    #     widget=forms.TextInput({'autofocus': 'autofocus'}))

    def __init__(self, *args, **kwargs):
        super(VendasPorForm, self).__init__(*args, **kwargs)
        self.order_fields([
            # 'cnpj',
            'ref',
        ])


class AnaliseModeloForm(
        O2BaseForm,
        O2FieldModeloForm):

    class Meta:
        autofocus_field = 'modelo'


class FaturamentoParaMetaForm(forms.Form):
    ano = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))
    mes = forms.IntegerField(required=False)

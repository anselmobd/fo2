from django import forms

from produto.forms import O2BaseForm, O2FieldRefForm


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

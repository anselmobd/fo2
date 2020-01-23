from pprint import pprint
from django import forms


class CriaUsuarioForm(forms.Form):

    number_attrs = {
        'type': 'number;',
        }

    autofocus_attrs = {
        'autofocus': 'autofocus;',
        }

    codigo = forms.CharField(
        label='Código (matrícula)',
        required=True, max_length=5,
        widget=forms.TextInput(attrs={
            **autofocus_attrs, **number_attrs}))

    def clean_codigo(self):
        return self.cleaned_data['codigo'].upper().zfill(5)

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
        label='Código (matrícula)', required=True, max_length=5,
        widget=forms.TextInput(attrs={
            **autofocus_attrs, **number_attrs}))

    cpf = forms.CharField(
        label='CPF', required=False, max_length=11,
        widget=forms.HiddenInput())

    def clean_codigo(self):
        return self.cleaned_data['codigo'].zfill(5)

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf = cpf.lstrip('0')
        if len(cpf) == 0:
            return ''
        return cpf.zfill(11)

from pprint import pprint

from django import forms

from systextil.models.base import Empresa


class NotaFiscalForm(forms.Form):
    empresa = forms.ChoiceField(
        required=True, initial=None)
    nf = forms.CharField(
        label='Nota fiscal',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super(NotaFiscalForm, self).__init__(*args, **kwargs)

        CHOICES = []
        empresas = Empresa.objects.all().order_by('codigo_empresa')
        for empresa in empresas:
            CHOICES.append((
                empresa.codigo_empresa,
                f"{empresa.codigo_empresa}-{empresa.nome_fantasia}",
            ))
        self.fields['empresa'].choices = CHOICES

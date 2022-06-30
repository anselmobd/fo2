from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs

from systextil.models.base import Empresa


class NFRecebidaForm(forms.Form):
    a = FormWidgetAttrs()

    empresa = forms.ChoiceField(
        required=True,
        initial=None,
    )

    nf = forms.CharField(
        label='Nota fiscal',
        widget=forms.TextInput(
            attrs={
                **a.string,
                **a.autofocus,
            }
        )
    )

    nf_ser = forms.CharField(
        label='Série da NF',
        required=False,
        widget=forms.TextInput(
            attrs={
                **a.number,
            }
        )
    )

    cnpj = forms.CharField(
        label="CNPJ",
        help_text="(só dígitos; completo ou início)",
        required=False,
        widget=forms.TextInput(
            attrs={
                **a.string,
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super(NFRecebidaForm, self).__init__(*args, **kwargs)

        CHOICES = []
        empresas = Empresa.objects.all().order_by('codigo_empresa')
        for empresa in empresas:
            CHOICES.append((
                empresa.codigo_empresa,
                f"{empresa.codigo_empresa}-{empresa.nome_fantasia}",
            ))
        self.fields['empresa'].choices = CHOICES

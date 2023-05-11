from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs

from systextil.models.base import Empresa


__all__ = ['NfForm']


class NfForm(forms.Form):
    a = FormWidgetAttrs()

    empresa = forms.ChoiceField(
        required=True,
        initial=None,
    )

    nf = forms.CharField(
        label='Número da NF',
        widget=forms.TextInput(
            attrs={
                'size': 6,
                **a.number,
                **a.autofocus,
            }
        )
    )

    vol_inicial = forms.CharField(
        label='Caixa inicial',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **a.number,
            }
        )
    )

    vol_final = forms.CharField(
        label='Caixa final',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **a.number,
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super(NfForm, self).__init__(*args, **kwargs)

        CHOICES = []
        empresas = Empresa.objects.filter(
            codigo_empresa__in=(1,4)).order_by('codigo_empresa')
        for empresa in empresas:
            CHOICES.append((
                empresa.codigo_empresa,
                f"{empresa.codigo_empresa}-{empresa.nome_fantasia}",
            ))
        self.fields['empresa'].choices = CHOICES

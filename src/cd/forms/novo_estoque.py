from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.strings import (
    is_only_digits,
    only_alnum,
)


class NovoEstoqueForm(forms.Form):
    a = FormWidgetAttrs()

    endereco = forms.CharField(
        label='Endereço',
        min_length=1,
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                **a.string_upper,
                **a.autofocus,
            }
        )
    )

    op = forms.CharField(
        label='OP',
        min_length=1,
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                'type': 'number',
            }
        )
    )

    lote = forms.CharField(
        min_length=9,
        max_length=9,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 9,
                'type': 'number',
            }
        )
    )

    modelo = forms.CharField(
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'number',
            }
        )
    )

    referencia = forms.CharField(
        label='Referência',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                **a.string_upper,
                **a.placeholder_0,
            }
        )
    )

    cor = forms.CharField(
        required=False,
        min_length=1,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                **a.string_upper,
                **a.placeholder_0,
            }
        )
    )

    tam = forms.CharField(
        label='Tamanho',
        required=False,
        min_length=1,
        max_length=3,
        widget=forms.TextInput(
            attrs={
                'size': 3,
                **a.string_upper,
            }
        )
    )

    CHOICES = [
        ('el', "Endereço, lote"),
        ('mod', "Modelo, referência"),
    ]
    order = forms.ChoiceField(
        label='Ordenação',
        choices=CHOICES,
        initial='el',
    )

    # CHOICES = [
    #     ('-', "Não filtra"),
    #     ('s', "Endereçado"),
    #     ('n', "Não endereçado"),
    # ]
    # enderecado = forms.ChoiceField(
    #     label='No CD',
    #     choices=CHOICES,
    #     initial=' ',
    # )

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_referencia(self):
        cleaned = self.cleaned_data['referencia']
        if len(cleaned) == 0:
            cleaned = ''
        else:
            if (
                len(cleaned) > 1 and 
                cleaned[0].isalpha() and 
                is_only_digits(cleaned[1:])
            ):
                cleaned = cleaned[0].upper() + cleaned[1:].upper().zfill(4)
            else:
                cleaned = cleaned.upper().zfill(5)

        data = self.data.copy()
        data['referencia'] = cleaned
        self.data = data
        return cleaned

    def clean_cor(self):
        cleaned = self.cleaned_data['cor']
        if len(cleaned) == 0:
            cleaned = ''
        else:
            cleaned = cleaned.upper().zfill(6)

        data = self.data.copy()
        data['cor'] = cleaned
        self.data = data
        return cleaned

    def clean_tam(self):
        cleaned = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = cleaned
        self.data = data
        return cleaned

    def clean_endereco(self):
        cleaned = only_alnum(
            self.cleaned_data.get('endereco', '')
        ).upper()
        data = self.data.copy()
        data['endereco'] = cleaned
        self.data = data
        return cleaned

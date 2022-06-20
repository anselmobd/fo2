from pprint import pprint

from django import forms

from fo2.connections import db_cursor_so

from comercial.queries import get_tabela_preco
from systextil.models import Colecao

from utils.functions.strings import is_only_digits


class DisponibilidadeFicticioForm(forms.Form):
    CHOICES = [
        ('g', 'Todas as grades'),
        ('d', 'Apenas grades de disponibilidade'),
        ('t', 'Apenas grades totais'),
    ]
    apresenta = forms.ChoiceField(
        choices=CHOICES, initial='t')

    modelo = forms.CharField(
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'number',
                'placeholder': '0',
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
                'type': 'string',
                'style': 'text-transform:uppercase;',
                'placeholder': '0...',
            }
        )
    )

    CHOICES_PAGINADOR = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    usa_paginador = forms.ChoiceField(
        label='Utiliza paginador',
        choices=CHOICES_PAGINADOR, initial='s')

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

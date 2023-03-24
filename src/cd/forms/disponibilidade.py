from pprint import pprint

from django import forms

from fo2.connections import db_cursor_so

from comercial.queries import get_tabela_preco
from systextil.models import Colecao

from utils.functions.strings import is_only_digits


class DisponibilidadeForm(forms.Form):
    CHOICES = [
        ('g', 'Todas as grades'),
        ('d', 'Apenas grades de disponibilidade'),
        ('t', 'Apenas grades totais'),
    ]
    apresenta = forms.ChoiceField(
        choices=CHOICES, initial='t')

    colecao = forms.ChoiceField(
        label='Coleção da referência',
        required=False, initial=None)

    tabela = forms.ChoiceField(
        label='Modelos da tabela de preços',
        required=False, initial=None)

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

    CHOICES = [
        ('p 63', 'Lotes paletizados com quantidade no 63-CD'),
        ('n <63', 'Lotes não paletizados com quantidade antes do 63-CD'),
        ('* *', 'Lotes independente de ser paletizado com quantidade em qualquer estágio'),
        ('* <63', 'Lotes independente de ser paletizado com quantidade antes do 63-CD'),
    ]
    tipo_inventario = forms.ChoiceField(
        label='Inventário',
        choices=CHOICES,
        initial='p 63'
    )

    corte_de = forms.DateField(
        label='Data de corte inicial', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    corte_ate = forms.DateField(
        label='Data de corte final', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    CHOICES_PAGINADOR = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    usa_paginador = forms.ChoiceField(
        label='Utiliza paginador',
        choices=CHOICES_PAGINADOR, initial='s')

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DisponibilidadeForm, self).__init__(*args, **kwargs)

        cursor = db_cursor_so(self.request)

        CHOICES = [(None, '(Todas)')]
        colecoes = Colecao.objects.all().order_by('colecao')
        for colecao in colecoes:
            CHOICES.append((
                colecao.colecao,
                f"{colecao.colecao}-{colecao.descr_colecao}"
            ))
        self.fields['colecao'].choices = CHOICES

        CHOICES_TABELA = [(None, '--')]
        tabelas = get_tabela_preco(cursor, col=1, mes=1, order='d')
        for tabela in tabelas:
            codigo_tabela = "{:02d}.{:02d}.{:02d}".format(
                tabela['col_tabela_preco'],
                tabela['mes_tabela_preco'],
                tabela['seq_tabela_preco'],
            )
            CHOICES_TABELA.append((
                codigo_tabela,
                f"{codigo_tabela}-{tabela['descricao']}"
            ))
        self.fields['tabela'].choices = CHOICES_TABELA

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

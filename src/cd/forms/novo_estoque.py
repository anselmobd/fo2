from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.strings import (
    is_only_digits,
    only_alnum,
)

from systextil.models import Colecao


class NovoEstoqueForm(forms.Form):
    a = FormWidgetAttrs()

    endereco = forms.CharField(
        label='Endereço',
        min_length=1,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 20,
                **a.string_upper,
                **a.autofocus,
            }
        )
    )

    # palete = forms.CharField(
    #     min_length=1,
    #     required=False,
    #     widget=forms.TextInput(
    #         attrs={
    #             'size': 6,
    #             **a.string_upper,
    #         }
    #     )
    # )

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

    solicitacoes = forms.CharField(
        label='Solicitações',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 40,
                'type': 'text',
            }
        )
    )

    colecao = forms.ChoiceField(
        label='Coleção da referência',
        required=False, initial=None)

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
        ('pagb', '* PA/PG/PB'),
        ('pgb', 'PG/PB'),
        ('pa', 'PA'),
        ('pg', 'PG'),
        ('pb', 'PB'),
        ('md', 'MD'),
        ('todos', 'Todos'),
    ]
    tipo_prod = forms.ChoiceField(
        label='Tipo de produto',
        choices=CHOICES,
        initial='pagb',
    )

    CHOICES = [
        ('63', "* Com estágio 63 (CD)"),
        ('n63', "Sem estágio 63 (CD)"),
        ('t', "Não filtra"),
    ]
    selecao_ops = forms.ChoiceField(
        label='Seleção de OPs',
        choices=CHOICES,
        initial='qq',
    )

    CHOICES = [
        ('63', "* Com quantidade no estágio 63 (CD)"),
        ('qq', "Com quantidade em qualquer estágio"),
        ('n63', "Com quantidade em estágio diferente de 63 (CD)"),
        ('605763', "Com quantidade nos estágios 60, 57 e 63 (EMBALAGEM, ARMAZENA e CD)"),
        ('60', "Com quantidade no estágio 60 (EMBALAGEM)"),
        ('57', "Com quantidade no estágio 57 (ARMAZENA)"),
        ('fin', "Lote finalizado"),
    ]
    selecao_lotes = forms.ChoiceField(
        label='Seleção de lotes',
        choices=CHOICES,
        initial='63',
    )

    CHOICES = [
        ('t', "* Não filtra"),
        ('esnf', "Empenhado ou solicitado não finalizado"),
        ('enf', "Empenhado não finalizado"),
        ('snf', "Solicitado não finalizado"),
        ('esf', "Empenhado/solicitado finalizado"),
    ]
    situacao_empenho = forms.ChoiceField(
        label='Situação de empenho',
        choices=CHOICES,
        initial='t',
    )

    CHOICES = [
        ('t', "* Não filtra"),
        ('ce', "Com empenho"),
        ('te', "Totalmente empenhado"),
        ('nte', "Não totalmente empenhado"),
        ('pe', "Parcialmente empenhado"),
        ('se', "Sem empenho"),
    ]
    qtd_empenhada = forms.ChoiceField(
        label='Filtra total empenhado',
        choices=CHOICES,
        initial='t',
    )

    CHOICES = [
        ('-', "* Não filtra"),
        ('t', "Solicitação total"),
        ('tp', "Solicitação total ou parcial"),
        ('p', "Solicitação parcial"),
        ('pn', "Solicitação parcial ou não solicitado"),
        ('n', "Não solicitado"),
    ]
    qtd_solicitada = forms.ChoiceField(
        label='Filtro por quantidade solicitada',
        choices=CHOICES,
        initial='-',
    )

    CHOICES = [
        ('s', "* Exige palete"),
        ('63', "Exige palete apenas no 63"),
        ('n', "Exige não ter palete"),
        ('t', "Não filtra"),
    ]
    paletizado = forms.ChoiceField(
        choices=CHOICES,
        initial='s',
    )

    CHOICES = [
        ('el', "Endereço, lote"),
        ('mod', "Modelo, item, endereço, lote"),
        ('emp', "Modelo, item, qtd. solicitada, endereço, lote"),
    ]
    order = forms.ChoiceField(
        label='Ordenação',
        choices=CHOICES,
        initial='el',
    )

    CHOICES_PLT_DT = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    palete_dt = forms.ChoiceField(
        label='Mostra data/hora de bipagem do lote no palete',
        choices=CHOICES_PLT_DT,
        initial='n',
    )

    CHOICES_PAGINADOR = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    usa_paginador = forms.ChoiceField(
        label='Utiliza paginador',
        choices=CHOICES_PAGINADOR,
        initial='s',
    )

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(NovoEstoqueForm, self).__init__(*args, **kwargs)

        CHOICES = [(None, '(Todas)')]
        colecoes = Colecao.objects.all().order_by('colecao')
        for colecao in colecoes:
            CHOICES.append((
                colecao.colecao,
                f"{colecao.colecao}-{colecao.descr_colecao}"
            ))
        self.fields['colecao'].choices = CHOICES

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
        cleaned = self.cleaned_data.get('endereco', '').strip().upper()
        data = self.data.copy()
        data['endereco'] = cleaned
        self.data = data
        return cleaned

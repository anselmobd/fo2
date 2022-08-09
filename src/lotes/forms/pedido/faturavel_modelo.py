from email.policy import default
from pprint import pprint

from django import forms

from systextil.models import Colecao


class Form(forms.Form):
    modelo = forms.CharField(
        label='Modelo',
        max_length=5,
        min_length=1,
        required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'autofocus': 'autofocus'
            }
        )
    )

    colecao = forms.ChoiceField(
        label='Coleção',
        required=False,
        initial=None,
    )

    tam = forms.CharField(
        label='Tamanho',
        required=False,
        widget=forms.TextInput(attrs={'type': 'string'})
    )

    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'})
    )

    CHOICES = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    considera_lead = forms.ChoiceField(
        label='Considera configuração de lead',
        choices=CHOICES,
        initial='s',
        required=False,
    )

    CHOICES = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    considera_pacote = forms.ChoiceField(
        label='Considera pacote do modelo',
        choices=CHOICES,
        initial='s',
        required=False,
        help_text='(quando filtrado por modelo)',
    )

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        colecoes = Colecao.objects.exclude(
            colecao=0
        ).order_by(
            'colecao'
        )
        self.fields['colecao'].choices = [(None, '(Todas)')] + [
            (
                colecao.colecao,
                f"{colecao.colecao}-{colecao.descr_colecao}"
            )
            for colecao in colecoes
        ] if colecoes else []
        self.fields['colecao'].empty_label="(Todas)"

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor

    def clean(self):
        if self.errors:
            return
        clean_form = super(Form, self).clean()
        if not any(
            clean_form.get(x, '')
            for x in (
                'modelo',
                'colecao',
                'tam',
                'cor',
            )
        ):
            raise forms.ValidationError(
                "Ao menos um dos filtros deve ser definido.")

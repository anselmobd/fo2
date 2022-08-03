from pprint import pprint

from django import forms

from systextil.models import Colecao


class Form(forms.Form):
    modelo = forms.CharField(
        label='Modelo', max_length=5, min_length=1, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    colecao = forms.ModelChoiceField(
        label='Coleção', required=False,
        queryset=Colecao.objects.exclude(colecao=0).order_by(
            'colecao'), empty_label="(Todas)")

    tam = forms.CharField(
        label='Tamanho', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    cor = forms.CharField(
        label='Cor', required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    considera_lead = forms.ChoiceField(
        label='Considera configuração de lead', choices=CHOICES, initial='s')

    CHOICES = [('s', 'Sim'),
               ('n', 'Não'),
               ]
    considera_pacote = forms.ChoiceField(
        label='Considera pacote do modelo',
        choices=CHOICES,
        initial='n',
        help_text='(quando filtrado por modelo)',
    )

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

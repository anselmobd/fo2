from pprint import pprint

from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs


class RealocaSolicitacoesForm(forms.Form):
    a = FormWidgetAttrs()

    field_control = [
        ['endereco'],
        ['solicitacoes'],
        ['modelo', 'cor', 'tam'],
        ['qtd_empenhada'],
        ['trab_sol_tot'],
        ['trab_sol_tot_dest'],
        ['forca_oti'],
        ['lotes_atendimento'],
    ]

    endereco = forms.CharField(
        label='Endereço destino',
        required=False,
        min_length=1,
        widget=forms.TextInput(
            attrs={
                'size': 30,
                **a.string_upper,
                **a.autofocus,
            }
        )
    )

    solicitacoes = forms.CharField(
        label='Solicitações',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 50,
                'type': 'text',
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
        ('ce', "Com empenho"),
        ('pe', "Parcialmente empenhado"),
    ]
    qtd_empenhada = forms.ChoiceField(
        label='Quantidade empenhada',
        choices=CHOICES,
        initial='s',
    )

    CHOICES = [
        ('n', "Não"),
        ('s', "Sim"),
    ]
    trab_sol_tot = forms.ChoiceField(
        label='Trabalha lotes com solicitações totais?',
        choices=CHOICES,
        initial='s',
    )

    CHOICES = [
        ('n', "Não"),
        ('s', "Sim"),
    ]
    trab_sol_tot_dest = forms.ChoiceField(
        label='Trabalha lotes com solicitações totais no destino?',
        choices=CHOICES,
        initial='n',
    )

    CHOICES = [
        ('n', "Não"),
        ('s', "Sim"),
    ]
    forca_oti = forms.ChoiceField(
        label='Força botão "Otimiza" após comparativo?',
        choices=CHOICES,
        initial='n',
    )

    lotes_atendimento = forms.CharField(
        label='Atender com o lotes ordenados',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 50,
                'type': 'text',
            }
        )
    )

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

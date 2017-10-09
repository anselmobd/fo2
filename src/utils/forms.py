from django import forms


class FiltroForm(forms.Form):
    busca = forms.CharField(
        label='Filtro', required=False,
        help_text='Busca vários valores separados por espaço.',
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_busca(self):
        busca = self.cleaned_data['busca'].upper()
        data = self.data.copy()
        data['busca'] = busca
        self.data = data
        return busca

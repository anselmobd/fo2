from django import forms


class RefForm(forms.Form):
    ref = forms.CharField(
        label='Referência', max_length=5, min_length=5,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class ModeloForm(forms.Form):
    modelo = forms.CharField(
        label='Modelo', max_length=4, min_length=3,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class ListaProdutoForm(forms.Form):
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

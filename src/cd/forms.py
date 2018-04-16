from django import forms


class LoteForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', min_length=2, max_length=3,
        widget=forms.TextInput())
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        if not endereco[0].isalpha():
            raise forms.ValidationError(
                "Deve iniciar com uma letra.")
        if not endereco[1:].isdigit():
            raise forms.ValidationError(
                "Depois da letra inicial deve ter apenas números.")
        return endereco

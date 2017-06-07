from django import forms


class LoteForm(forms.Form):
    lote = forms.CharField(label='Lote', max_length=9, min_length=9,
                           widget=forms.TextInput(attrs={'type': 'number'}))

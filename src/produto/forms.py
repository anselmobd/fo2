from django import forms


class RefForm(forms.Form):
    ref = forms.CharField(
        label='Referência',
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

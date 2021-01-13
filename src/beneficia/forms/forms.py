from django import forms


class ObForm(forms.Form):
    ob = forms.CharField(
        label='OB',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

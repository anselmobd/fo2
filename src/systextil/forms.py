from django import forms

__all__=['MinutosForm']


class MinutosForm(forms.Form):
    minutos = forms.IntegerField(
        initial=60,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

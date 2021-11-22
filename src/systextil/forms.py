from django import forms

__all__=['SegundosForm']


class SegundosForm(forms.Form):
    segundos = forms.IntegerField(
        initial=60,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

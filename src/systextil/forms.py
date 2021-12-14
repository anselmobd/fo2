from django import forms

__all__=['SegundosForm']


class SegundosForm(forms.Form):
    segundos = forms.IntegerField(
        label='Executando a quantos segundos?',
        initial=60,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))


class SessaoForm(forms.Form):
    id = forms.IntegerField(
        label='ID de sessão',
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

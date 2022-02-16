from django import forms

__all__=['SegundosForm', 'SessaoForm']


class SegundosForm(forms.Form):
    segundos = forms.IntegerField(
        label='Executando há quantos segundos?',
        initial=60,
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))


class SessaoForm(forms.Form):
    sessao_id = forms.IntegerField(
        label='ID de sessão',
        widget=forms.NumberInput(attrs={'autofocus': 'autofocus'}))

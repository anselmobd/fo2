from django import forms

from .models import Pop


class PainelModelForm(forms.ModelForm):
    layout = forms.CharField(
        label='Layout',
        widget=forms.Textarea(
            attrs={'max_length': 4096, 'rows': 10, 'cols': 79}))


class InformacaoModuloModelForm(forms.ModelForm):
    texto = forms.CharField(
        label='texto',
        widget=forms.Textarea(
            attrs={'max_length': 4096, 'rows': 10, 'cols': 79}))


class InformacaoModuloForm(forms.Form):
    chamada = forms.CharField(
        widget=forms.Textarea(
            attrs={'max_length': 200, 'rows': 5, 'cols': 39,
                   'style': 'vertical-align:top;'}))
    habilitado = forms.BooleanField(required=False)


class PopForm(forms.ModelForm):
    class Meta:
        model = Pop
        fields = ('descricao', 'pop', 'habilitado')

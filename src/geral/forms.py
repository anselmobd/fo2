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
        help_text='(máximo 200 caracteres)',
        widget=forms.Textarea(
            attrs={'max_length': 200, 'rows': 5, 'cols': 39,
                   'style': 'vertical-align:top;'}))
    habilitado = forms.BooleanField(required=False)


class PopForm(forms.ModelForm):
    class Meta:
        model = Pop
        fields = ('assunto', 'descricao', 'pop', 'habilitado')


class GeraFluxoDotForm(forms.Form):
    id = forms.CharField(
        label='Fluxo', max_length=3, min_length=1,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    CHOICES = [('t', 'Tela'),
               ('a', 'Arquivo'),
               ]
    destino = forms.ChoiceField(
        label='Gera arquivo para', choices=CHOICES, initial='t')

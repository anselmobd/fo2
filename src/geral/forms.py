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


class GeraRoteirosRefForm(forms.Form):
    ref = forms.CharField(
        label='Referência', max_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

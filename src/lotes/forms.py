from django import forms


class LoteForm(forms.Form):
    lote = forms.CharField(label='Lote', max_length=9, min_length=9,
                           widget=forms.TextInput(attrs={'type': 'number'}))


class ResponsPorEstagioForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    usuario = forms.CharField(
        label='Usuário', max_length=20, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    CHOICES = [('e', 'Por estágio'),
               ('u', 'Por usuário')]
    ordem = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

    def clean_usuario(self):
        return self.cleaned_data['usuario'].upper()

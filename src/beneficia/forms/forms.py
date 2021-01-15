from django import forms


class ObForm(forms.Form):
    ob = forms.CharField(
        label='OB',
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'autofocus': 'autofocus'
            }
        )
    )


class BuscaObForm(forms.Form):
    periodo = forms.CharField(
        label='Período', required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'size': 4,
                'autofocus': 'autofocus'
            }
        )
    )
    obs = forms.CharField(
        label='Observação', required=False,
        widget=forms.TextInput(),
        help_text='(parte)'
    )
    ot = forms.CharField(
        label='OT', required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'size': 5,
            }
        )
    )
    ref = forms.CharField(
        label='Referencia a produzir', required=False,
        widget=forms.TextInput(attrs={'size': 5})
    )

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

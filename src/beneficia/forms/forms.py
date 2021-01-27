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
    ordens = forms.CharField(
        label='OBs', required=False,
        widget=forms.TextInput(),
        help_text='(Ex.: -2, 4, 6, 8-10, 12-  )'
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
    ob2 = forms.CharField(
        label='OB2', required=False,
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

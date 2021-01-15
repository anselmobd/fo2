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
            }
        )
    )
    ref = forms.CharField(
        label='Referencia a produzir', required=False,
        widget=forms.TextInput()
    )

from django import forms

__all__=['ZeraSenhaForm']


class ZeraSenhaForm(forms.Form):
    login = forms.CharField(
        min_length=1,
        max_length=20,
        widget=forms.TextInput()
    )

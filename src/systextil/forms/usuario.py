from django import forms

from systextil.models.base import Empresa

__all__=['ZeraSenhaForm']


class ZeraSenhaForm(forms.Form):
    empresa = forms.ChoiceField(
        required=True, initial=None)
    login = forms.CharField(
        label="Usuário (login)",
        min_length=1,
        max_length=20,
        widget=forms.TextInput()
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.get('request', None)
        super(ZeraSenhaForm, self).__init__(*args, **kwargs)

        CHOICES = []
        empresas = Empresa.objects.all().order_by('codigo_empresa')
        for empresa in empresas:
            CHOICES.append((
                empresa.codigo_empresa,
                f"{empresa.codigo_empresa}-{empresa.nome_fantasia}",
            ))
        self.fields['empresa'].choices = CHOICES

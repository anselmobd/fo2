from pprint import pprint
from django import forms


class UploadArquivoForm(forms.Form):
    arquivo = forms.FileField()

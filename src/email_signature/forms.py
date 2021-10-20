from datetime import datetime, timedelta
from pprint import pprint

from django import forms

from utils.functions import shift_years

from .models import *


class AccountForm(forms.ModelForm):

    email = forms.CharField(
        widget=forms.TextInput(attrs={"size": 40, "autofocus": "autofocus"}))

    nome = forms.CharField(
        widget=forms.TextInput(attrs={"size": 40}))

    ddd_1 = forms.CharField(
        widget=forms.NumberInput(attrs={"size": 2, "min": 1}))

    ddd_2 = forms.CharField(
        widget=forms.NumberInput(attrs={"size": 2, "min": 1}))

    subdiretorio = forms.CharField(
        widget=forms.TextInput(attrs={"size": 40}))

    class Meta:
        model = Account
        fields = [
            "email", "nome", "setor",
            "ddd_1", "num_1", "ddd_2", "num_2",
            "diretorio", "subdiretorio"
        ]

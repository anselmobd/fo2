from django import forms

from itat.models import DhcpConfig


class DhcpConfigForm(forms.ModelForm):
    primary_template = forms.CharField(
        label=DhcpConfig._meta.get_field(
            'primary_template').verbose_name,
        widget=forms.Textarea(
            attrs={'max_length': 65535, 'rows': 20, 'cols': 79}))
    secondary_template = forms.CharField(
        label=DhcpConfig._meta.get_field(
            'secondary_template').verbose_name,
        widget=forms.Textarea(
            attrs={'max_length': 65535, 'rows': 20, 'cols': 79}))

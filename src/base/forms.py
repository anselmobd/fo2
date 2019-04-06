from pprint import pprint
import re

from django import forms


class O2BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self, 'Meta'):

            if hasattr(self.Meta, 'order_fields'):
                self.order_fields(self.Meta.order_fields)

            if hasattr(self.Meta, 'required_fields'):
                self.required_fields(self.Meta.required_fields)

            if hasattr(self.Meta, 'autofocus_field'):
                self.autofocus_field(self.Meta.autofocus_field)

    def saver(self, field_name, field):
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def cleanner_field(self, field):
        field = field.upper()
        field = re.search('[A-Z0-9]+', field).group(0)
        return field

    def cleanner(self, field_name):
        field = self.cleaned_data[field_name]
        if field != '':
            field = self.cleanner_field(field)
        return self.saver(field_name, field)

    def cleanner_pad_field(self, field, length):
        field = self.cleanner_field(field)
        field = field.lstrip('0')
        field = field.zfill(length)
        return field

    def cleanner_pad(self, field_name, length):
        field = self.cleaned_data[field_name]
        if field != '':
            field = self.cleanner_pad_field(field, length)
        return self.saver(field_name, field)

    def required_fields(self, fields):
        for field in fields:
            self.fields[field].required = True

    def autofocus_field(self, field):
        fields = list(self.fields)
        for a_field in fields:
            attrs = self.fields[a_field].widget.attrs
            if a_field == field:
                attrs.update({'autofocus': 'autofocus'})
            else:
                if 'autofocus' in attrs:
                    attrs.pop('autofocus')


class O2FieldRefForm(forms.Form):
    ref = forms.CharField(
        label='Referência',
        required=False,
        widget=forms.TextInput(attrs={'size': 5}))

    def clean_ref(self):
        return O2BaseForm.cleanner_pad(self, 'ref', 5)


class O2FieldTamanhoForm(forms.Form):
    tamanho = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 3}))

    def clean_tamanho(self):
        return O2BaseForm.cleanner(self, 'tamanho')


class O2FieldCorForm(forms.Form):
    cor = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 6}))

    def clean_cor(self):
        return O2BaseForm.cleanner_pad(self, 'cor', 6)


class O2FieldGtinForm(forms.Form):
    gtin = forms.CharField(
        label='GTIN', max_length=13, min_length=13, required=False,
        widget=forms.TextInput(attrs={'size': 13}))

    def clean_cor(self):
        return O2BaseForm.cleanner(self, 'gtin')

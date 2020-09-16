from pprint import pprint
import re

from django import forms

from utils.decorators import method_idle_on_none


class O2BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.process_meta(getattr(self, 'Meta', None))

    @method_idle_on_none
    def process_meta(self, meta):
        self.order_fields(getattr(meta, 'order_fields', None))

        self.required_fields(getattr(meta, 'required_fields', None))

        self.autofocus_field(getattr(meta, 'autofocus_field', None))

        self.initial_values(getattr(meta, 'initial_values', None))

    def saver(self, field_name, field):
        data = self.data.copy()
        data[field_name] = field
        self.data = data
        return field

    def upper(self, field_name):
        field = self.cleaned_data[field_name]
        if field != '':
            field = field.upper()
        return self.saver(field_name, field)

    def cleanner_field(self, field, field_type='an'):
        field = field.upper()
        field_type_re = '[A-Z0-9]'
        if field_type == 'a':
            field_type_re = '[A-Z]'
        elif field_type == 'n':
            field_type_re = '[0-9]'
        field = re.search(f'{field_type_re}+', field).group(0)
        return field

    def cleanner(self, field_name, field_type='an'):
        field = self.cleaned_data[field_name]
        if field != '':
            field = self.cleanner_field(field, field_type=field_type)
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

    @method_idle_on_none
    def required_fields(self, fields):
        for field in fields:
            self.fields[field].required = True

    @method_idle_on_none
    def autofocus_field(self, field):
        fields = list(self.fields)
        for a_field in fields:
            attrs = self.fields[a_field].widget.attrs
            if a_field == field:
                attrs.update({'autofocus': 'autofocus'})
            else:
                if 'autofocus' in attrs:
                    attrs.pop('autofocus')

    @method_idle_on_none
    def initial_values(self, initials):
        for initial in initials:
            self.fields[initial].initial = initials[initial]

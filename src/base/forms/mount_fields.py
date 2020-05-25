from pprint import pprint

from django import forms


def MountTypeFieldForm(type_field, field, attrs, widget_attrs):
    field_form = type_field(attrs)
    field_form.widget.attrs = widget_attrs
    return type(
        "MountedTypeFieldForm",
        (forms.Form, ),
        {field: field_form, }
    )


def MountIntegerFieldForm(field, attrs={}, widget_attrs={}):
    return MountTypeFieldForm(forms.IntegerField, field, attrs, widget_attrs)

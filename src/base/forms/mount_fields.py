from pprint import pprint

from django import forms


def MountTypeFieldForm(
        field, attrs=None, widget_attrs={},
        type_field=forms.CharField, widget=None):

    kwargs = {'required': False}
    if attrs is not None:
        kwargs.update(attrs)
    if widget is not None:
        kwargs['widget'] = widget(widget_attrs)

    field_form = type_field(**kwargs)

    if widget is None:
        field_form.widget.attrs = widget_attrs

    return type(
        "MountedTypeFieldForm",
        (forms.Form, ),
        {field: field_form, }
    )


def MountIntegerFieldForm(field, **kwargs):
    return MountTypeFieldForm(field, **kwargs, type_field=forms.IntegerField)


def MountNumberFieldForm(field, attrs={}, widget_attrs={}):
    return MountTypeFieldForm(
        field, **kwargs, type_field=forms.CharField,
        widget=forms.NumberInput)

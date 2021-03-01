from pprint import pprint

from django import forms


def MountTypeFieldForm(
        name, attrs=None, widget_attrs={},
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
        {name: field_form, }
    )


def MountIntegerFieldForm(name, **kwargs):
    return MountTypeFieldForm(name, **kwargs, type_field=forms.IntegerField)


def MountDateFieldForm(name, **kwargs):
    return MountTypeFieldForm(
        name, **kwargs, type_field=forms.DateField,
        widget=forms.DateInput, widget_attrs={'type': 'date'})


def MountNumberFieldForm(name, attrs={}, widget_attrs={}):
    return MountTypeFieldForm(
        name, **kwargs, type_field=forms.CharField,
        widget=forms.NumberInput)


def MountCharFieldForm(name, **kwargs):
    return MountTypeFieldForm(name, **kwargs, type_field=forms.CharField)

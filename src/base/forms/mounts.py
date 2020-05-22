from django import forms

from base.forms import custom
from base.forms import fields


def MountForm(*args, **kwargs):
    '''
        args: são os inputs do form
            - string: referência a uma classe em classes (abaixo)
        kwargs: são atributos da subclasse Meta do form
    '''
    classes = {
        'deposito': fields.O2FieldDepositoForm,
        'pedido': MountIntegerFieldForm('pedido'),
    }

    superclasses = custom.O2BaseForm,
    for field in args:
        superclasses += classes[field],

    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )


def MountTypeFieldForm(type_field, field):
    field_form = type_field()
    return type(
        "MountedTypeFieldForm",
        (forms.Form, ),
        {field: field_form, }
    )


def MountIntegerFieldForm(field):
    return MountTypeFieldForm(forms.IntegerField, field)

from pprint import pprint

from base.forms import custom
from base.forms import fields


class ModeloForm(
        custom.O2BaseForm,
        fields.O2FieldModeloForm):

    class Meta:
        autofocus_field = 'modelo'


class DepositoForm(
        custom.O2BaseForm,
        fields.O2FieldDepositoForm):

    class Meta:
        autofocus_field = 'deposito'

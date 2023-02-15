from pprint import pprint

from base.forms import (
    custom,
    fields2,
    mount_fields,
)


def MountForm(field=None, **kwargs):
    '''
        field: caso o form tenha apenas um input, é o nome do campo
            de outra forma os campos estão definidos no kwargs['fields']
        kwargs: são atributos da subclasse Meta do form
    '''

    field_classes = {
        'deposito': fields2.Fields2().Deposito,
        'colecao': fields2.Fields2().Colecao,
        'modelo': fields2.Fields2().Modelo,
        'pedido': fields2.Fields2().Pedido,
        'referencia': fields2.Fields2().Referencia,
    }

    if field:
        fields = [{'name': field}]
    else:
        fields = kwargs.pop('fields')

    order_fields = []
    superclasses = custom.O2BaseForm,

    for field in fields:
        name = field.pop('name')
        order_fields.append(name)

        if field == {}:
            field_class = field_classes[name]
        else:
            attrs = {}
            if 'label' in field:
                attrs.update({'label': field['label']})
            if field['type'] == 'date':
                field_class = mount_fields.MountDateFieldForm(
                    name,
                    attrs=attrs,
                )
        superclasses += field_class,

    kwargs['order_fields'] = order_fields
    Meta = type('MountedMeta', (object, ), kwargs)

    return type(
        "MountedDepositoForm",
        superclasses,
        {'Meta': Meta, }
    )

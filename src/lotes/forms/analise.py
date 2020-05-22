from base.forms.forms import MountForm


def MountModeloForm():
    return MountForm(
        'deposito',
        autofocus_field='deposito'
    )

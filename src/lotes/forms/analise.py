from base.forms.mounts import MountForm


def MountModeloForm():
    return MountForm(
        'deposito',
        autofocus_field='deposito'
    )

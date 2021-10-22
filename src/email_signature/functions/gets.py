from pprint import pprint

import email_signature.models as models


def get_template(tipo):
    try:
        return models.Layout.objects.get(
            habilitado=True,
            tipo=tipo,
        ).template
    except Exception:
        return


def get_template_file(tipo=None):
    template = get_template(tipo)
    if template is not None:
        return f'email_signature/{template}.html'

from pprint import pprint

import email_signature.models as models


def processor(context):
    return {
        'email_signature_tipos': dict(models._TIPO_CHOICES),
    }

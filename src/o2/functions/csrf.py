from pprint import pprint

from django.db import IntegrityError

import o2.models


def save_csrf(token):
    try:
        csrf_token = o2.models.CsrfToken(token=token)
        csrf_token.save()
        return True
    except IntegrityError:
        return False


def csrf_used(request):
    if request.method == "POST":
        token = request.POST['csrfmiddlewaretoken']
        return not save_csrf(token)
    return False

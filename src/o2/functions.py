from pprint import pprint

import o2.models


def csrf_used(request):
    if request.method == "POST":
        token = request.POST['csrfmiddlewaretoken']
        try:
            o2.models.CsrfToken.objects.get(token=token)
            return True
        except o2.models.CsrfToken.DoesNotExist:
            csrf_token = o2.models.CsrfToken(token=token)
            csrf_token.save()
    return False

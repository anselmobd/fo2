from .models import Painel


# http://kkabardi.me/post/dynamic-menu-navigation-django/
def get_list_geral_paineis(context):
    p = Painel.objects.all()
    return {'list_geral_paineis': p}

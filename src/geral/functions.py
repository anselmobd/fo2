from .models import Painel, PainelModulo


# http://kkabardi.me/post/dynamic-menu-navigation-django/
def get_list_geral_paineis(context):
    paineis = Painel.objects.all()
    modulos = PainelModulo.objects.all().order_by('nome')
    return {'list_geral_paineis': paineis,
            'list_geral_modulos': modulos,
            }


def request_user(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    return user


def has_permission(request, permission):
    can = False
    user = request_user(request)
    if user:
        can = user.has_perm(permission)
    return can

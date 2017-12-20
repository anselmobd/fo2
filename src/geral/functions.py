from .models import Painel, PainelModulo


# http://kkabardi.me/post/dynamic-menu-navigation-django/
def get_list_geral_paineis(context):
    paineis = Painel.objects.all()
    modulos = PainelModulo.objects.all()
    return {'list_geral_paineis': paineis,
            'list_geral_modulos': modulos,
            }

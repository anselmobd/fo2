from pprint import pprint

from base.models import Colaborador


def get_create_colaborador_by_user(user):
    try:
        colab = Colaborador.objects.get(user__username=user.username)
    except Colaborador.DoesNotExist:
        colab = Colaborador(
            user=user,
            matricula=72000+user.id,
            cpf=72000+user.id,
        )
        colab.save()
    return colab

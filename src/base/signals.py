from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import Colaborador


@receiver(user_logged_in)
def login_user(sender, user, request, **kwargs):
    try:
        colab = Colaborador.objects.get(user__username=user.username)
        colab.logged = True
        colab.save()
    except Colaborador.DoesNotExist:
        pass


@receiver(user_logged_out)
def logout_user(sender, user, request, **kwargs):
    try:
        colab = Colaborador.objects.get(user__username=user.username)
        colab.logged = False
        colab.save()
    except Colaborador.DoesNotExist:
        pass

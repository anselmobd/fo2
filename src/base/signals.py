from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone

from .models import Colaborador


@receiver(user_logged_in)
def login_user(sender, user, request, **kwargs):
    try:
        colab = Colaborador.objects.get(user__username=user.username)
    except Colaborador.DoesNotExist:
        colab = Colaborador(
            user=user,
            matricula=72000+user.id,
            cpf=72000+user.id,
        )
        colab.save()

    try:
        colab.logged = True
        colab.quando = timezone.now()
        colab.save()
    except Exception:
        pass


@receiver(user_logged_out)
def logout_user(sender, user, request, **kwargs):
    try:
        colab = Colaborador.objects.get(user__username=user.username)
        colab.logged = False
        colab.quando = timezone.now()
        colab.save()
    except Colaborador.DoesNotExist:
        pass

from django.db import models
from django.utils import timezone


class Account(models.Model):
    codigo = models.CharField(
        max_length=20, unique=True, verbose_name='código')
    nome = models.CharField(
        null=True, blank=True,
        max_length=100)
    setor = models.CharField(
        null=True, blank=True,
        max_length=100)
    email = models.CharField(
        null=True, blank=True,
        max_length=100, verbose_name='e-mail')
    tipo_num_1 = models.CharField(
        null=True, blank=True,
        max_length=20, verbose_name='tipo do número 1')
    num_1 = models.CharField(
        null=True, blank=True,
        max_length=20, verbose_name='número 1')
    tipo_num_2 = models.CharField(
        null=True, blank=True,
        max_length=20, verbose_name='tipo do número 2')
    num_2 = models.CharField(
        null=True, blank=True,
        max_length=20, verbose_name='número 2')
    dir_servidor = models.CharField(
        null=True, blank=True,
        max_length=200, verbose_name='diretório no servidor')
    dir_local = models.CharField(
        null=True, blank=True,
        max_length=200, verbose_name='diretório no local')
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Criada em')
    update_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='alterado em')

    def __str__(self):
        return self.codigo

    def save(self, *args, **kwargs):
        ''' On create, get timestamps '''
        now = timezone.now()
        if self.id:
            self.update_at = now
        else:  # At create have no "id"
            self.create_at = now
        super(Account, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_emsign_account"
        verbose_name = "Conta"
        permissions = (("can_edit_mail_signature", "Can edit mail signature"),
                       )

from datetime import datetime, timedelta
from pprint import pprint

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

import remote_files.models


_TIPO_CHOICES = [
    ('tussor', 'Tussor'),
    ('agator' ,'Agator'),
]
_STATE_CHOICES = [
    ('R', 'Gerar'),
    ('N', 'Gerando'),
    ('A', 'Gerada'),
]


class Account(models.Model):
    tipo = models.CharField(
        max_length=10,
        choices=_TIPO_CHOICES,
        default=_TIPO_CHOICES[0][0],
    )
    email = models.EmailField(
        unique=True,
        max_length=100, verbose_name='e-mail')
    nome = models.CharField(
        max_length=100)
    setor = models.CharField(
        null=True, blank=True,
        max_length=100)
    ddd_1 = models.IntegerField(
        default=21, verbose_name='DDD 1')
    num_1 = models.CharField(
        null=True, blank=True,
        max_length=20, verbose_name='número 1')
    ddd_2 = models.IntegerField(
        default=21, verbose_name='DDD 2')
    num_2 = models.CharField(
        null=True, blank=True,
        max_length=20, verbose_name='número 2')
    cnpj = models.BooleanField(
        default=False,
        verbose_name='Apresenta CNPJ')
    diretorio = models.ForeignKey(
        remote_files.models.Diretorio, on_delete=models.PROTECT)
    subdiretorio = models.CharField(
        max_length=200, verbose_name='sub-diretório de assinatura')
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Criada em')
    update_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='alterado em')
    state = models.CharField(
        max_length=1,
        choices=_STATE_CHOICES,
        default=_STATE_CHOICES[0][0],
        verbose_name='Estado')


    def __str__(self):
        setor = '' if self.setor is None else f' ({self.setor})'
        return f'{dict(_TIPO_CHOICES)[self.tipo]} - {self.email} - {self.nome}{setor}'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.id:  # At update have "id"
            if self.state == 'N':  # Alteração foi de indicação de "GeraNdo"
                self.state = 'A'  # Marca assinatura como "GeradA
            else:  # Outras alterações
                self.update_at = now
                self.state = 'R'  # Marca assinatura como "GeraR"
        else:  # At create have no "id"
            self.create_at = now
        super(Account, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_emsign_account"
        verbose_name = "Conta"
        permissions = (("can_edit_mail_signature", "Can edit mail signature"),
                       )


class Layout(models.Model):
    tipo = models.CharField(
        max_length=10,
        choices=_TIPO_CHOICES,
        default=_TIPO_CHOICES[0][0],
    )
    nome = models.CharField(
        max_length=64)
    slug = models.SlugField()
    template = models.CharField(
        max_length=64)
    habilitado = models.BooleanField(
        default=False)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_emsign_layout"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.tipo}-{self.nome}")
        super(Layout, self).save(*args, **kwargs)
        if self.habilitado:
            outros_habilitados = Layout.objects.filter(
                habilitado=True,
                tipo=self.tipo,
            ).exclude(id=self.id)
            for layout in outros_habilitados:
                layout.habilitado = False
                layout.save()

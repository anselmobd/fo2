import datetime
from pprint import pprint

from django.contrib.auth.models import User
from django.db import models


class EstoquePermissions(models.Model):

    class Meta:
        managed = False
        permissions = (
            ("can_transferencia", "Pode fazer transferência entre depósitos"),
        )


class TipoMovStq(models.Model):
    codigo = models.CharField(
        max_length=100, unique=True, default="-",
        verbose_name='Código')
    descricao = models.CharField(
        max_length=100,
        verbose_name='Descrição')
    trans_saida = models.IntegerField(
        default=0,
        verbose_name='Transação de saída')
    trans_entrada = models.IntegerField(
        default=0,
        verbose_name='Transação de entrada')

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fo2_est_tipo_mov"
        verbose_name = "Tipo de movimento de estoque"
        verbose_name_plural = "Tipos de movimentos de estoque"


_doc_mov_stq_start_range = 802000000


class DocMovStqManager(models.Manager):
    def get_queryset(self):
        return super(
            DocMovStqManager,
            self).get_queryset().annotate(
                num_doc=models.F('id') + _doc_mov_stq_start_range).all()


class DocMovStq(models.Model):
    descricao = models.CharField(
        max_length=100,
        verbose_name='Descrição')
    data = models.DateField()
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='usuário')

    objects = DocMovStqManager()

    def __str__(self):
        return f'{self.num_doc} - {self.descricao}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.data = datetime.date.today()
        super(DocMovStq, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_est_doc_mov"
        verbose_name = "Documento de movimento de estoque"
        verbose_name_plural = "Documentos de movimentos de estoque"

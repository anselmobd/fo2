from pprint import pprint

from django.db import models


class MetaPermissions(models.Model):

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

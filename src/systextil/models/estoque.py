from django.db import models

from systextil.models.base import HDoc001


class ContaEstoque(models.Model):
    conta_estoque = models.IntegerField(
        primary_key=True,
        verbose_name='Código')
    descr_ct_estoque = models.CharField(
        max_length=100,
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}'.format(self.conta_estoque, self.descr_ct_estoque)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_150"
        verbose_name = "Conta de estoque"


class TipoContaEstoqueManager(models.Manager):
    def get_queryset(self):
        return super(
            TipoContaEstoqueManager, self).get_queryset().filter(tipo=420)


class TipoContaEstoque(HDoc001):
    objects = TipoContaEstoqueManager()

    def __str__(self):
        return '{}-{}'.format(self.codigo, self.descricao)

    class Meta:
        proxy = True
        managed = False
        app_label = 'systextil'
        db_table = "HDOC_001"
        verbose_name = "Tipo de conta de estoque"


class TipoTransacao(models.Model):
    codigo_transacao = models.IntegerField(
        primary_key=True,
        verbose_name='Código da transação')
    descricao = models.CharField(
        max_length=20,
        verbose_name='Descrição')

    def __str__(self):
        return '{} - {}'.format(self.codigo_transacao, self.descricao)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "ESTQ_005"
        verbose_name = "Código de transação de estoque"

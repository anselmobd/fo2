from pprint import pprint

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Inventario(models.Model):
    inicio = models.DateTimeField(
        verbose_name='início',
    )

    def __str__(self):
        return self.inicio.strftime("%d/%m/%Y %H:%M")

    def save(self, *args, **kwargs):
        # se não tem ID, é inserção
        if not self.id:
            self.inicio = timezone.now()

        super(Inventario, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_inventario"
        verbose_name = "Inventário"


class InventarioLote(models.Model):
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        verbose_name='inventário',
    )
    lote = models.CharField(
        db_index=True,
        max_length=9,
    )
    quantidade = models.IntegerField(
        default=0,
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='informado por',
    )
    quando = models.DateTimeField(
        verbose_name='informado em',
    )
    diferenca = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='direrença',
    )
    # versao = models.IntegerField(
    #     default=0,
    #     verbose_name='versão')
    # corrigido_por = models.ForeignKey(
    #     User,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     verbose_name='corrigido por',
    # )
    # corrigido_inicio = models.DateTimeField(
    #     null=True,
    #     blank=True,
    #     verbose_name='início da correção',
    # )
    # corrigido_fim = models.DateTimeField(
    #     null=True,
    #     blank=True,
    #     verbose_name='fim da correção',
    # )

    def save(self, *args, **kwargs):
        # se tem "id" é alteração
        # if self.id:
        #     raise QtdEmLote.DoesNotExist
        #     for qel in QtdEmLote.objects.filter(lote=self.lote)                        

        # se não tem "id" é inclusão
        if not self.id:
            self.inventario=Inventario.objects.order_by('inicio').last()
            self.quando = timezone.now()

        super(InventarioLote, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_inventario_lote"
        verbose_name = "Inventário de lote"
        unique_together = [["lote", "quando"]]

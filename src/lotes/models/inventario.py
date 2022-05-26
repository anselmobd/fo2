from pprint import pprint

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# class InventarioLote(models.Model):
#     lote = models.CharField(
#         db_index=True,
#         max_length=9,
#     )
#     quantidade = models.IntegerField(
#         default=0,
#     )
#     usuario = models.ForeignKey(
#         User,
#         on_delete=models.PROTECT,
#         verbose_name='informado por',
#     )
#     quando = models.DateTimeField(
#         verbose_name='informado em',
#     )
#     # versao = models.IntegerField(
#     #     default=0,
#     #     verbose_name='versão')
#     # corrigido_por = models.ForeignKey(
#     #     User,
#     #     on_delete=models.PROTECT,
#     #     null=True,
#     #     blank=True,
#     #     verbose_name='corrigido por',
#     # )
#     # corrigido_inicio = models.DateTimeField(
#     #     null=True,
#     #     blank=True,
#     #     verbose_name='início da correção',
#     # )
#     # corrigido_fim = models.DateTimeField(
#     #     null=True,
#     #     blank=True,
#     #     verbose_name='fim da correção',
#     # )

#     def save(self, *args, **kwargs):
#         # # se tem "id" é alteração
#         # if self.id:
#         #     raise QtdEmLote.DoesNotExist
#         #     for qel in QtdEmLote.objects.filter(lote=self.lote)                        
#         self.quando = timezone.now()

#         super(InventarioLote, self).save(*args, **kwargs)

#     class Meta:
#         db_table = "fo2_inventario_lote"
#         verbose_name = "Inventário de lote"

from pprint import pprint

from django.utils import timezone
from django.db import models


class LotesPermissions(models.Model):

    class Meta:
        managed = False
        permissions = (
            ("can_edit_estagio_direito", "Can edit direitos a estágios"),
            ("can_print__solicitacao_parciais",
             "Pode imprimir etiquetas de solicitações parciais"),
        )


# Abaixo: estudos do TableHeap
class TableHeapManager(models.Manager):
    def get_queryset(self):
        return super(TableHeapManager, self).get_queryset().filter(origin_id=0)


# Testada sem o "abstract = True" e funcionou bem
class TableHeap(models.Model):
    origin_id = models.IntegerField(
        default=0,
        verbose_name='id de origem')
    deleted = models.NullBooleanField(
        default=False,
        verbose_name='apagado')
    version = models.IntegerField(
        default=0,
        verbose_name='versão')
    when = models.DateTimeField(
        null=True, blank=True,
        verbose_name='quando')
    unique_aux = models.IntegerField(
        default=0,
        verbose_name='campo auxiliar para unique_together')

    objects_all = models.Manager()
    objects = TableHeapManager()

    def save_old(self, id, deleted=False):
        try:
            old = TableHeap.objects.get(id=id)
            old.origin_id = old.id
            old.unique_aux = old.version
            old.id = None
            old.deleted = deleted
            old.save()
        except Exception:
            pass

    def save(self, *args, **kwargs):
        if self.id:
            self.save_old(self.id)
        self.when = timezone.now()
        if self.origin_id == 0:
            self.version += 1
        super(TableHeap, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.save_old(self.id, deleted=True)
        super(TableHeap, self).delete(*args, **kwargs)

    class Meta:
        abstract = True
        # db_table = "fo2_table_head"
        verbose_name = "Tabela com pilha de versões"

# Não funcionou a tabala abaixo
# class TableCodes(TableHeap):
#     code = models.CharField(
#         max_length=20,
#         verbose_name='código')
#
#     def __init__(self):
#         self.unique_together = ('code', 'origin_id', 'unique_aux',)
#
#     class Meta:
#         db_table = "fo2_codes"
#         verbose_name = "Tabela herdando pilha de versões"

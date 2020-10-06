from pprint import pprint

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Op(models.Model):
    op = models.IntegerField(
        verbose_name='OP')
    pedido = models.IntegerField()
    varejo = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    deposito = models.IntegerField(default=-1)

    class Meta:
        db_table = "fo2_prod_op"
        permissions = (("can_repair_seq_op", "Can repair sequence OP"),
                       )


class Caixa(models.Model):
    caixa = models.CharField(
        max_length=20)
    TIPOS_DE_CAIXAS = (('o', 'OP'), ('a', 'Avulsa'))
    tipo_doc = models.CharField(
        max_length=1, choices=TIPOS_DE_CAIXAS,
        default='o', verbose_name='tipo de documento')
    id_doc = models.CharField(
        max_length=64, null=True, blank=True,
        verbose_name='identificador do documento')
    ordem = models.IntegerField(
        null=True, blank=True,
        verbose_name='ordem da caixa')
    ativa = models.NullBooleanField(default=True)
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='criada em')
    update_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='alterado em')

    def save(self, *args, **kwargs):
        ''' On create and update, get timestamps '''
        now = timezone.now()
        if self.id:
            self.update_at = now
        else:  # At create have no "id"
            self.create_at = now
        return super(Caixa, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_caixa"
        verbose_name = "caixa"


class Lote(models.Model):
    lote = models.CharField(
        db_index=True, max_length=20, verbose_name='lote')
    op = models.IntegerField(
        db_index=True, null=True, blank=True, verbose_name='OP')
    op_obj = models.ForeignKey(
        Op, null=True, default=None, on_delete=models.PROTECT)
    referencia = models.CharField(
        db_index=True, max_length=5, verbose_name='Referência')
    tamanho = models.CharField(
        db_index=True, max_length=3, verbose_name='Tamanho')
    ordem_tamanho = models.IntegerField(
        db_index=True, default=0, verbose_name='ordem tamanho')
    cor = models.CharField(
        db_index=True, max_length=6, verbose_name='Cor')
    qtd_produzir = models.IntegerField(
        verbose_name='quantidade a produzir')
    estagio = models.IntegerField(
        db_index=True, default=0)
    qtd = models.IntegerField(
        default=0, verbose_name='quantidade em produçao ou produzida')
    conserto = models.IntegerField(
        default=0, verbose_name='quantidade em conserto')
    create_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name='criado em')
    update_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name='alterado em')
    local = models.CharField(
        db_index=True, null=True, blank=True, default=None, max_length=4)
    local_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name='localizado em')
    local_usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='localizado por')
    caixa = models.ForeignKey(
        Caixa, null=True, default=None, on_delete=models.CASCADE)
    trail = models.IntegerField(default=0)

    __original_local = None

    def __init__(self, *args, **kwargs):
        super(Lote, self).__init__(*args, **kwargs)
        self.__original_local = self.local

    def save(self, *args, **kwargs):
        ''' On create and update, get timestamps '''
        now = timezone.now()

        if self.id:
            self.update_at = now
            if self.local or self.__original_local:
                if self.__original_local != self.local:
                    self.local_at = now
        else:  # At create have no "id"
            self.create_at = now

        if self.op_obj is None:
            try:
                self.op_obj = Op.objects.get(op=self.op)
            except Exception:
                pass

        return super(Lote, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_lote"
        verbose_name = "lote"
        permissions = (("can_inventorize_lote", "Can inventorize lote"),
                       ("can_relocate_lote", "Can relocate lote"),
                       ("can_uninventorize_road", "Can uninventorize road"),
                       )


# class LoteCaixa(models.Model):
#     lote = models.ForeignKey(
#         Lote, on_delete=models.CASCADE)
#     caixa = models.ForeignKey(
#         Caixa, on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = "fo2_cd_caixa_lote"
#         verbose_name = "lote na caixa"

from pprint import pprint

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from base.models import (
    Colaborador,
)
from utils.classes import LoggedInUser


class Op(models.Model):
    op = models.IntegerField(
        verbose_name='OP')
    pedido = models.IntegerField()
    varejo = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    deposito = models.IntegerField(default=-1)
    sync_id = models.IntegerField(default=-1)
    sync = models.IntegerField(default=-1)

    class Meta:
        db_table = "fo2_prod_op"
        permissions = (
            ("can_repair_seq_op", "Can repair sequence OP"),
            ("can_reactivate_op", "Can reactivate OP"),
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
    ativa = models.BooleanField(
        default=True)
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
        db_index=True, null=True, blank=True, default=None, max_length=5)
    local_at = models.DateTimeField(
        db_index=True, null=True, blank=True, verbose_name='localizado em')
    local_usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name='localizado por')
    caixa = models.ForeignKey(
        Caixa, null=True, default=None, on_delete=models.PROTECT)
    trail = models.IntegerField(default=0)
    sync_id = models.IntegerField(default=-1)
    sync = models.IntegerField(default=-1)

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
#         Lote, on_delete=models.PROTECT)
#     caixa = models.ForeignKey(
#         Caixa, on_delete=models.PROTECT)
#
#     class Meta:
#         db_table = "fo2_cd_caixa_lote"
#         verbose_name = "lote na caixa"


# TableHeap - Managers definitions - start
class OpCortadaActiveManager(models.Manager):
    def get_queryset(self):
        return super(
            OpCortadaActiveManager,
            self).get_queryset().filter(log=0)


class OpCortadaDeletedManager(models.Manager):
    def get_queryset(self):
        return super(
            OpCortadaDeletedManager,
            self).get_queryset().filter(version__isnull=True)
# TableHeap - Managers definitions - end


class OpComCorte(models.Model):

    # class Evento(models.TextChoices):
    #     CORTADA = 'C', 'OP cortada'
    #     PEDIDO_FM = 'F', 'Pedido de venda da filial para a matriz'
    #     PEDIDO_CM = 'M', 'Pedido de compra na matriz'
    #     NF = 'N', 'Gera NF de pedido da filial'
    #     NF_REC = 'R', 'Recebe NF da filial na matriz'

    op = models.IntegerField(
        verbose_name="OP",
    )
    cortada_colab = models.ForeignKey(
        Colaborador,
        verbose_name="Cortada colaborador",
        on_delete=models.PROTECT,
        # related_name='cortado_colabuser_table_heap1',
    )
    cortada_quando = models.DateTimeField(
        verbose_name="Cortada quando",
        default=timezone.now,
    )
    pedido_fm_num = models.IntegerField(
        verbose_name="Pedido-FM número",
        null=True,
        blank=True,
    )

    # evento = models.CharField(
    #     max_length=1,
    #     choices=Evento.choices,
    #     default=Evento.CORTADA,
    # )

    # TableHeap - Fields - start
    log = models.IntegerField(
        default=0,
        verbose_name='log',
    )
    version = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name='versão',
    )
    when = models.DateTimeField(
        default=timezone.now,
        verbose_name='quando',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='usuário',
        related_name='user_table_heap1',
    )
    # TableHeap - Fields - end

    # TableHeap - Assigning managers - start
    objects = OpCortadaActiveManager()
    objects_deleted = OpCortadaDeletedManager()
    objects_all = models.Manager()
    # TableHeap - Assigning managers - end

    # TableHeap - Save functions - start
    def save_log(self, id):
        log = OpComCorte.objects.get(id=id)
        log.log = log.id
        log.id = None
        log.save()

    def save_deleted(self, id):
        self.save_log(id)
        deleted = OpComCorte.objects.get(id=id)
        deleted.log = deleted.id
        deleted.version = None
        deleted.when = timezone.now()
        deleted.user = LoggedInUser().user
        deleted.id = None
        deleted.save()
    # TableHeap - Save functions - end

    def save(self, *args, **kwargs):
        # TableHeap - start
        if self.id:  # is update
            self.save_log(self.id)
        if not self.log:  # não é registro de log
            self.version += 1
            self.when = timezone.now()
            self.user = LoggedInUser().user
        # TableHeap - end
        super(OpComCorte, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # TableHeap - start
        self.save_deleted(self.id)
        # TableHeap - end
        super(OpComCorte, self).delete(*args, **kwargs)

    class Meta:
        db_table = "fo2_op_com_corte"
        verbose_name = "OP com corte"
        verbose_name_plural = "OPs com corte"
        permissions = (
            ("pode_marcar_op_como_cortada", "Pode marcar OP como cortada"),
        )

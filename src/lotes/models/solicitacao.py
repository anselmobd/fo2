from pprint import pprint

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

from utils.functions.digits import fo2_digit_with

from lotes.models.op import Lote


class SolicitaLote(models.Model):
    codigo = models.CharField(
        unique=True, max_length=20,
        verbose_name='código')
    descricao = models.CharField(
        max_length=200, null=True, blank=True,
        verbose_name='descrição')
    data = models.DateField(
        null=True, blank=True,
        verbose_name='Data do embarque')
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='usuário')
    ativa = models.NullBooleanField(default=True)
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='criado em')
    update_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='alterado em')
    concluida = models.BooleanField(
        default=False,
        verbose_name='Solicitação concluída')
    can_print = models.BooleanField(
        default=True,
        verbose_name='Pode imprimir')
    coleta = models.BooleanField(
        default=False,
        verbose_name='Pode coletar')

    @property
    def numero(self):
        return fo2_digit_with(self.id)

    def __str__(self):
        return f"#{self.numero}: {self.codigo} ({self.descricao})"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo and self.codigo.upper()
        ''' On create and update, get timestamps '''
        now = timezone.now()
        self.update_at = now
        # At create have no "id"
        if not self.id:
            self.create_at = now
        super(SolicitaLote, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_solicita_lote"
        verbose_name = "Solicitação de lote"


# class EstadoSolicitacao(models.Model):
#     nome = models.CharField(
#         max_length=20,
#         db_index=True, unique=True)
#
#     def __str__(self):
#         return self.nome
#
#     class Meta:
#         db_table = "fo2_!!pos_carga"
#         verbose_name = "Posição de carga(NF)"
#         verbose_name_plural = "Posições de carga(NF)"


class SolicitaLoteQtdActiveManager(models.Manager):
    def get_queryset(self):
        return super(
            SolicitaLoteQtdActiveManager,
            self).get_queryset().filter(origin_id=0)


class SolicitaLoteQtdInactiveManager(models.Manager):
    def get_queryset(self):
        return super(
            SolicitaLoteQtdInactiveManager,
            self).get_queryset().exclude(origin_id=0)


class SolicitaLoteQtd(models.Model):
    solicitacao = models.ForeignKey(
        SolicitaLote, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Solicitação')
    lote = models.ForeignKey(
        Lote, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Lote')
    qtd = models.IntegerField(
        default=0, verbose_name='quantidade solicitada')
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='criado em')
    update_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='alterado em')

    # Table Heap
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
        verbose_name='quando')
    unique_aux = models.IntegerField(
        default=0,
        verbose_name='campo auxiliar para unique_together')

    # TableHeap - "objects" filter only active rows
    objects = SolicitaLoteQtdActiveManager()
    objects_inactive = SolicitaLoteQtdInactiveManager()
    objects_all = models.Manager()

    # TableHeap - heap constructor
    def save_old(self, id, deleted=False):
        try:
            old = SolicitaLoteQtd.objects.get(id=id)
            old.origin_id = old.id
            old.unique_aux = old.version
            old.id = None
            old.deleted = deleted
            old.save()
        except Exception:
            pass

    def save(self, *args, **kwargs):
        # TableHeap start
        if self.id:
            self.save_old(self.id)
        self.when = timezone.now()
        if self.origin_id == 0:
            self.version += 1
        # TableHeap end

        self.update_at = self.when
        if not self.id:
            self.create_at = self.when

        super(SolicitaLoteQtd, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # TableHeap start
        self.save_old(self.id, deleted=True)
        # TableHeap end

        super(SolicitaLoteQtd, self).delete(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_solicita_lote_qtd"
        verbose_name = "Quantidades Solicitadas de lotes"


class SolicitaLotePrinted(models.Model):
    solicitacao = models.ForeignKey(
        SolicitaLote, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Solicitação')
    printed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='etiquetas impressas em')
    printed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='etiquetas impressas por')

    def save(self, *args, **kwargs):
        if not self.id:
            self.printed_at = timezone.now()
        super(SolicitaLotePrinted, self).save(*args, **kwargs)
        self.solicitacao.can_print = False
        self.solicitacao.save()

    class Meta:
        db_table = "fo2_cd_solicita_lote_prt"
        verbose_name = "Impressão de solicitação de lotes"
        verbose_name_plural = "Impressões de solicitações de lotes"

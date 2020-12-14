import datetime
from pprint import pprint

from django.contrib.auth.models import User
from django.db import models

from produto.models import ProdutoItem


class EstoquePermissions(models.Model):

    class Meta:
        verbose_name = 'Permissões de estoque'
        managed = False
        permissions = (
            ("can_transferencia", "Pode fazer transferência entre depósitos"),
        )


class TipoMovStq(models.Model):
    codigo = models.CharField(
        'Código',
        max_length=100, unique=True, default="-")
    descricao = models.CharField(
        'Descrição',
        max_length=100)
    trans_saida = models.IntegerField(
        'Transação de saída',
        default=0)
    trans_entrada = models.IntegerField(
        'Transação de entrada',
        default=0)
    menu = models.BooleanField(
        'Aparece no menu',
        default=False)
    ordem = models.IntegerField(
        default=0)
    renomeia = models.BooleanField(
        'Renomeia',
        default=False)
    CHOICES = (
        ('1', '1 para 1'),
        ('M', 'Monta Kit'),
        ('D', 'Desmonta Kit'),
    )
    unidade = models.CharField(
        max_length=1, choices = CHOICES, default='1')

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
        'Descrição',
        max_length=100)
    data = models.DateField()
    usuario = models.ForeignKey(
        User, models.PROTECT,
        verbose_name='usuário')

    objects = DocMovStqManager()

    @property
    def get_num_doc(self):
        return self.id + _doc_mov_stq_start_range

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


class MovStq(models.Model):
    tipo_mov = models.ForeignKey(
        TipoMovStq, models.PROTECT,
        verbose_name='Tipo de movimento')
    item = models.ForeignKey(
        ProdutoItem, models.PROTECT)
    quantidade = models.IntegerField(
        default=0)
    deposito_origem = models.IntegerField(
        'Depósito de origem')
    deposito_destino = models.IntegerField(
        'Depósito de destino')
    novo_item = models.ForeignKey(
        ProdutoItem, models.PROTECT, related_name='movstqdest', null=True)
    documento = models.ForeignKey(
        DocMovStq, models.PROTECT,
        verbose_name='Documento de movimento de estoque')
    usuario = models.ForeignKey(
        User, models.PROTECT,
        verbose_name='usuário')
    obs = models.CharField(
        'Observação', default='',
        max_length=100)
    hora = models.DateTimeField(
        null=True, auto_now_add=True)

    def __str__(self):
        return (f'{self.documento.get_num_doc}, {self.item} '
                f'{self.deposito_origem}->{self.deposito_destino}')

    class Meta:
        db_table = "fo2_est_mov"
        verbose_name = "Movimento de estoque"
        verbose_name_plural = "Movimentos de estoque"

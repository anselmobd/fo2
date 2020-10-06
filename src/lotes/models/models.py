from pprint import pprint

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from utils.functions.digits import *

from .op import *


class LotesPermissions(models.Model):

    class Meta:
        managed = False
        permissions = (
            ("can_edit_estagio_direito", "Can edit direitos a estágios"),
            ("can_print__solicitacao_parciais",
             "Pode imprimir etiquetas de solicitações parciais"),
        )


class Impresso(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')
    slug = models.SlugField()

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impresso"
        verbose_name = "Impresso"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(Impresso, self).save(*args, **kwargs)


class ModeloTermica(models.Model):
    codigo = models.CharField(
        unique=True, max_length=20, null=True, blank=True,
        verbose_name='código')
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='nome')

    # Tive problemas com esse campo pois ficou com tamanho 2048, sem forma
    # de definir novo tamanho. Tive que passar para CharField
    # modelo = models.TextField(
    #     null=True, blank=True,
    #     verbose_name='modelo')

    # Tive problemas novamente. Mensagem reclamendo de 2048. Não entendi.
    # Só criando outro campo consegui voltar ao trabalho.
    # receita = models.CharField(
    #     null=True, blank=True, max_length=8192,
    #     verbose_name='receita')

    gabarito = models.CharField(
        null=True, blank=True, max_length=8192,
        verbose_name='gabarito')
    campos = models.TextField(
        null=True, blank=True,
        verbose_name='campos')

    def __str__(self):
        return self.codigo

    class Meta:
        db_table = "fo2_lot_modelo_termica"
        verbose_name = "modelo de etiqueta térmica"
        verbose_name_plural = "modelos de etiqueta térmica"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo and self.codigo.upper()
        super(ModeloTermica, self).save(*args, **kwargs)


class ImpressoraTermica(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impr_termica"
        verbose_name = "impressora térmica"
        verbose_name_plural = "impressoras térmicas"


class UsuarioImpresso(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    impresso = models.ForeignKey(
        Impresso, on_delete=models.CASCADE,
        verbose_name='impresso')
    impressora_termica = models.ForeignKey(
        ImpressoraTermica, on_delete=models.CASCADE,
        verbose_name='impressora térmica')
    modelo = models.ForeignKey(
        ModeloTermica, on_delete=models.CASCADE,
        verbose_name='modelo padrão')

    class Meta:
        db_table = "fo2_lot_usuario_impresso"
        verbose_name = "Impressos de usuário"
        verbose_name_plural = "Impressos de usuários"
        unique_together = ("usuario", "impresso")


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


class LeadColecao(models.Model):
    colecao = models.IntegerField(
        primary_key=True,
        verbose_name='Coleção')
    lead = models.IntegerField(
        null=True, blank=True, default=0)
    lm_tam = models.IntegerField(
        null=True, blank=True, default=0,
        verbose_name='Lote mínimo por tamanho')
    lm_cor = models.IntegerField(
        null=True, blank=True, default=0,
        verbose_name='Lote mínimo por cor')

    def __str__(self):
        return '{}-{}'.format(self.colecao, self.lead)

    class Meta:
        db_table = "fo2_lot_lead_colecao"
        verbose_name = "Lead de produção"
        verbose_name_plural = "Leads de produção"


class RegraLMTamanho(models.Model):
    tamanho = models.CharField(
        primary_key=True,
        max_length=3,
        verbose_name='Tamanho')

    ordem_tamanho = models.IntegerField(
        null=True, blank=True, default=0,
        verbose_name='Ordem do tamanho')

    min_para_lm = models.IntegerField(
        null=True, blank=True, default=0,
        verbose_name='% mínimo para aplicação do lote mínimo por tamanho')

    lm_cor_sozinha = models.CharField(
        max_length=1, default='s',
        verbose_name='Aplica lote mínimo por cor quando único tamanho')

    def __str__(self):
        return self.tamanho

    class Meta:
        db_table = "fo2_lot_regra_lm_tamanho"
        verbose_name = "Regra de lote mínimo por tamanho"

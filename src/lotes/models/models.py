from pprint import pprint

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Familia(models.Model):
    divisao_producao = models.IntegerField(primary_key=True)
    descricao = models.CharField(
        max_length=20,
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}'.format(self.divisao_producao, self.descricao)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_180"
        verbose_name = "Família"


class Impresso(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impresso"
        verbose_name = "Impresso"


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


class Op(models.Model):
    op = models.IntegerField(
        verbose_name='OP')
    pedido = models.IntegerField()
    varejo = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)

    class Meta:
        db_table = "fo2_prod_op"
        permissions = (("can_repair_seq_op", "Can repair sequence OP"),
                       )


class Lote(models.Model):
    lote = models.CharField(
        db_index=True, max_length=20, verbose_name='lote')
    op = models.IntegerField(
        db_index=True, null=True, blank=True, verbose_name='OP')
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
        return super(Lote, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_lote"
        verbose_name = "lote"
        permissions = (("can_inventorize_lote", "Can inventorize lote"),
                       ("can_relocate_lote", "Can relocate lote"),
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


class SolicitaLote(models.Model):
    codigo = models.CharField(
        unique=True, max_length=20,
        verbose_name='código')
    descricao = models.CharField(
        max_length=200, null=True, blank=True,
        verbose_name='descrição')
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

    objects_all = models.Manager()
    objects = SolicitaLoteQtdActiveManager()
    objects_inactive = SolicitaLoteQtdInactiveManager()

    def save(self, *args, **kwargs):
        ''' On create and update, get timestamps '''
        now = timezone.now()
        self.update_at = now
        # At create have no "id"
        if not self.id:
            self.create_at = now
        super(SolicitaLoteQtd, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_solicita_lote_qtd"
        verbose_name = "Quantidades Solicitadas de lotes"


# class ReservaLoteQtd(models.Model):
#     solicitacao = models.ForeignKey(
#         SolicitaLote, on_delete=models.CASCADE, null=True, blank=True,
#         verbose_name='Solicitação')
#     lote = models.ForeignKey(
#         Lote, on_delete=models.CASCADE, null=True, blank=True,
#         verbose_name='Lote')
#     qtd = models.IntegerField(
#         default=0, verbose_name='quantidade solicitada')
#
#     active = models.NullBooleanField(default=True)
#     create_at = models.DateTimeField(
#         null=True, blank=True,
#         verbose_name='criado em')
#     inactive_at = models.DateTimeField(
#         null=True, blank=True,
#         verbose_name='inativado em')
#
#     def save(self, *args, **kwargs):
#         ''' On create and update, get timestamps '''
#         if self.id:
#             # old = deepcopy(self)
#             old = ReservaLoteQtd.objects.get(id=self.id)
#             old.id = None
#             old.active = False
#             old.save()
#         now = timezone.now()
#         if self.active:
#             self.create_at = now
#         else:
#             self.inactive_at = now
#         super(ReservaLoteQtd, self).save(*args, **kwargs)
#
#     def delete(self, *args, **kwargs):
#         old = ReservaLoteQtd.objects.get(id=self.id)
#         old.id = None
#         old.active = False
#         old.save()
#         super(ReservaLoteQtd, self).delete(*args, **kwargs)
#
#     class Meta:
#         db_table = "fo2_reserva_lote_qtd"
#         verbose_name = "Quantidades reservadas de lotes"

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

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
        if self.id:
            self.update_at = timezone.now()
        else:  # At create have no "id"
            self.create_at = timezone.now()
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
        if self.id:
            self.update_at = timezone.now()
            if self.local or self.__original_local:
                if self.__original_local != self.local:
                    self.local_at = timezone.now()
        else:  # At create have no "id"
            self.create_at = timezone.now()
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
        self.update_at = timezone.now()
        # At create have no "id"
        if not self.id:
            self.create_at = timezone.now()
        super(SolicitaLote, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_solicita_lote"
        verbose_name = "Solicitação de lote"


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

    def save(self, *args, **kwargs):
        ''' On create and update, get timestamps '''
        self.update_at = timezone.now()
        # At create have no "id"
        if not self.id:
            self.create_at = timezone.now()
        super(SolicitaLoteQtd, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_solicita_lote_qtd"
        verbose_name = "Quantidades Solicitadas de lotes"

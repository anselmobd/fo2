from django.db import models


class Colecao(models.Model):
    colecao = models.IntegerField(primary_key=True)
    descr_colecao = models.CharField(
        max_length=100,
        verbose_name='Descrição')

    def __str__(self):
        return self.descr_colecao

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_140"
        verbose_name = "Coleção"


class GtinRange(models.Model):
    ordem = models.IntegerField(
        unique=True,
        verbose_name='Ordem de adoção do range')
    pais = models.CharField(
        max_length=3,
        verbose_name='Código do país do range')
    codigo = models.CharField(
        max_length=5, unique=True,
        verbose_name='Código identificador do range')

    def __str__(self):
        return '{} - ({}){}'.format(self.ordem, self.pais, self.codigo)

    class Meta:
        db_table = "fo2_gtin_range"
        verbose_name = "Range de GTIN"


class S_Produto(models.Model):
    nivel_estrutura = models.CharField(
        primary_key=True, max_length=1,
        verbose_name='Nível')
    referencia = models.CharField(
        primary_key=True, max_length=5,
        verbose_name='Referência')

    def __str__(self):
        return '{}.{}'.format(self.nivel_estrutura, self.referencia)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_030"
        verbose_name = "Produto (Systêxtil)"


class Produto(models.Model):
    referencia = models.CharField(
        db_index=True, max_length=5,
        verbose_name='Referência')
    ativo = models.BooleanField(default=True)
    imp_cod = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Código impresso')

    def __str__(self):
        ativo = '' if self.ativo else '--'
        return '{}{}'.format(ativo, self.referencia)

    class Meta:
        db_table = "fo2_produto"
        verbose_name = "Produto"


class ProdutoCor(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        verbose_name='Referência')
    cor = models.CharField(
        db_index=True, max_length=6, verbose_name='Cor')
    ativa = models.BooleanField(default=True)
    imp_cod = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Código impresso')
    imp_descr = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Descrição impressa')

    def __str__(self):
        ativa = '' if self.ativa else '--'
        return '{}({}) {}'.format(ativa, self.produto, self.cor)

    class Meta:
        db_table = "fo2_produto_cor"
        verbose_name = "Cor de um produto"
        verbose_name_plural = "Cores de um produto"


class ProdutoTamanho(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        verbose_name='Referência')
    tamanho = models.CharField(
        db_index=True, max_length=6)
    ativo = models.BooleanField(default=True)
    imp_cod = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Código impresso')
    imp_descr = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Descrição impressa')

    def __str__(self):
        ativo = '' if self.ativo else '--'
        return '{}({}) {}'.format(ativo, self.produto, self.tamanho)

    class Meta:
        db_table = "fo2_produto_tamanho"
        verbose_name = "Tamanho de um produto"
        verbose_name_plural = "Tamanhos de um produto"


class Composicao(models.Model):
    descricao = models.CharField(
        'descrição',
        max_length=200)

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fo2_composicao"
        verbose_name = "Composição"
        verbose_name_plural = "Composições"

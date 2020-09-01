from django.core.exceptions import ValidationError
from django.db import models

from base.models import (
    Colaborador,
    ImagemTag,
    Tamanho,
)


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


def validate_produto_nivel(value):
    if value in [1, 2, 9]:
        return value
    else:
        raise ValidationError("Nível deve ser 1, 2 ou 9")


class Produto(models.Model):
    nivel = models.IntegerField(
        db_index=True, validators=[validate_produto_nivel],
        verbose_name='Nível')
    referencia = models.CharField(
        db_index=True, max_length=5,
        verbose_name='Referência')
    descricao = models.CharField(
        'descrição', default='',
        max_length=200)
    ativo = models.BooleanField(default=True)
    imp_cod = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Código impresso')
    composicao = models.ForeignKey(
        Composicao, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Composição')
    imagem_tag = models.ForeignKey(
        ImagemTag, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Imagem no TAG')
    cor_no_tag = models.BooleanField(
        default=True, verbose_name='Imprime cor no TAG')
    ncm = models.CharField(
        max_length=8, default='',
        verbose_name='NCM')
    unidade = models.CharField(
        max_length=2, default='')

    @property
    def nivel_referencia(self):
        ativo = '' if self.ativo else '--'
        return f'{ativo}{self.nivel}.{self.referencia}'

    def __str__(self):
        ativo = '' if self.ativo else '--'
        return f'{ativo}{self.nivel}.{self.referencia} - {self.descricao}'

    class Meta:
        db_table = "fo2_produto"
        verbose_name = "Produto"


class ProdutoCor(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        verbose_name='Referência')
    cor = models.CharField(
        db_index=True, max_length=6, verbose_name='Cor')
    descricao = models.CharField(
        'descrição', default='',
        max_length=200)
    ativa = models.BooleanField(default=True)
    imp_cod = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Código impresso')
    imp_descr = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Descrição impressa')
    composicao = models.ForeignKey(
        Composicao, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Composição')

    def __str__(self):
        ativa = '' if self.ativa else '--'
        return (f'{ativa}({self.produto.nivel_referencia}) '
                f'{self.cor} - {self.descricao}')

    class Meta:
        db_table = "fo2_produto_cor"
        verbose_name = "Cor de um produto"
        verbose_name_plural = "Cores de um produto"


class ProdutoTamanho(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        verbose_name='Referência')
    tamanho = models.ForeignKey(
        Tamanho, on_delete=models.PROTECT)
    descricao = models.CharField(
        'descrição', default='',
        max_length=200)
    ativo = models.BooleanField(default=True)
    imp_cod = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Código impresso')
    imp_descr = models.CharField(
        max_length=6, null=True, blank=True,
        verbose_name='Descrição impressa')

    def __str__(self):
        ativo = '' if self.ativo else '--'
        return '{}({}) {}'.format(ativo, self.produto, self.tamanho.nome)

    class Meta:
        db_table = "fo2_produto_tamanho"
        verbose_name = "Tamanho de um produto"
        verbose_name_plural = "Tamanhos de um produto"


class ProdutoItem(models.Model):
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        verbose_name='Referência')
    cor = models.ForeignKey(
        ProdutoCor, on_delete=models.CASCADE)
    tamanho = models.ForeignKey(
        ProdutoTamanho, on_delete=models.CASCADE)
    gtin_tag = models.CharField(
        max_length=13, null=True, blank=True,
        verbose_name='GTIN no TAG')
    gtin = models.CharField(
        max_length=13, null=True, blank=True,
        verbose_name='GTIN no XML')
    custo = models.DecimalField(
        decimal_places=4, max_digits=12,
        null=True, blank=True)

    def __str__(self):
        return '{} {} {}'.format(
            self.produto.referencia, self.cor.cor, self.tamanho.tamanho.nome)

    class Meta:
        db_table = "fo2_produto_item"
        verbose_name = "Item do produto"
        verbose_name_plural = "Itens do produto"


class ComposicaoLinha(models.Model):
    composicao = models.ForeignKey(
        Composicao, on_delete=models.CASCADE,
        verbose_name='Composição')
    ordem = models.IntegerField()
    linha = models.CharField(max_length=100)

    def __str__(self):
        return '({}) {}: {}'.format(self.composicao, self.ordem, self.linha)

    class Meta:
        db_table = "fo2_composicao_linha"
        verbose_name = "Linha da Composição"
        verbose_name_plural = "Linhas da Composição"


class GtinLog(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.PROTECT)
    quando = models.DateTimeField(
        null=True, blank=True)
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE,
        verbose_name='Referência')
    cor = models.ForeignKey(
        ProdutoCor, on_delete=models.CASCADE)
    tamanho = models.ForeignKey(
        ProdutoTamanho, on_delete=models.CASCADE)
    gtin = models.CharField(
        max_length=13, null=True, blank=True,
        verbose_name='GTIN no XML')

    def __str__(self):
        return (f"1.{self.produto.referencia}."
                f"{self.tamanho.tamanho.nome}.{self.cor.cor} - {self.gtin} - "
                f"{self.quando} - {self.colaborador.user.username}")

    class Meta:
        db_table = "fo2_prod_gtin_log"
        verbose_name_plural = 'GTIN Log'
        permissions = (
            ("can_set_gtin", "Can set GTIN"),
        )

from django.utils import timezone
from django.db import models


class ContaEstoque(models.Model):
    conta_estoque = models.IntegerField(
        primary_key=True,
        verbose_name='Código')
    descr_ct_estoque = models.CharField(
        max_length=100,
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}'.format(self.conta_estoque, self.descr_ct_estoque)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_150"
        verbose_name = "Conta de estoque"


class PeriodoConfeccaoManager(models.Manager):
    def get_queryset(self):
        return super(PeriodoConfeccaoManager, self).get_queryset().filter(
            area_periodo=1)


class Periodo(models.Model):
    area_periodo = models.IntegerField(
        primary_key=True,
        verbose_name='Área do período')
    periodo_producao = models.IntegerField(
        primary_key=True,
        verbose_name='Período de produção')
    data_ini_periodo = models.DateTimeField(
        verbose_name='Data inicial do período')
    data_fim_periodo = models.DateTimeField(
        verbose_name='Data final do período')

    objects = models.Manager()
    confeccao = PeriodoConfeccaoManager()

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "PCPC_010"
        verbose_name = "Período"


class SugestaoCompra(models.Model):
    nivel = models.CharField(
        db_index=True, max_length=1,
        verbose_name='Nível')
    referencia = models.CharField(
        db_index=True, max_length=5,
        verbose_name='Referência')
    tamanho = models.CharField(
        db_index=True, max_length=3,
        verbose_name='Tamanho')
    ordem_tamanho = models.IntegerField(
        db_index=True, default=0,
        verbose_name='ordem tamanho')
    cor = models.CharField(
        db_index=True, max_length=6,
        verbose_name='Cor')
    data = models.DateTimeField(
        db_index=True,
        verbose_name='Data do calculo')
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Criada em')

    def save(self, *args, **kwargs):
        ''' On create, get timestamps '''
        # At create have no "id"
        if not self.id:
            self.create_at = timezone.now()
        super(SugestaoCompra, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_sugestao_compra"
        verbose_name = "Sugestão de compra"


class SugestaoCompraDatas(models.Model):
    sugestao = models.ForeignKey(
        SugestaoCompra, on_delete=models.CASCADE,
        db_index=True,
        verbose_name='Sugestão de compra')
    data_compra = models.DateField(
        db_index=True,
        verbose_name='Data de compra')
    data_recepcao = models.DateField(
        verbose_name='Data de recepção')
    qtd = models.DecimalField(
        max_digits=13, decimal_places=3,
        verbose_name='Quantidade')

    class Meta:
        db_table = "fo2_sugestao_compra_datas"
        verbose_name = "Datas da sugestão de compra"


class HDoc001(models.Model):
    tipo = models.IntegerField(
        primary_key=True)
    codigo = models.IntegerField(
        primary_key=True,
        verbose_name='Código')
    descricao = models.CharField(
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}-{}'.format(self.tipo, self.codigo, self.descricao)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "HDOC_001"
        verbose_name = "Tabela auxiliar HDOC_001"


class TipoContaEstoqueManager(models.Manager):
    def get_queryset(self):
        return super(
            TipoContaEstoqueManager, self).get_queryset().filter(tipo=420)


class TipoContaEstoque(HDoc001):
    objects = TipoContaEstoqueManager()

    def __str__(self):
        return '{}-{}'.format(self.codigo, self.descricao)

    class Meta:
        proxy = True
        managed = False
        app_label = 'systextil'
        db_table = "HDOC_001"
        verbose_name = "Tipo de conta de estoque"

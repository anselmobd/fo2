from django.db.models import Exists, OuterRef
from django.db import models


class ModeloPassado(models.Model):
    nome = models.CharField(
        max_length=50,
        db_index=True, unique=True)
    padrao = models.BooleanField(
        db_index=True, default=False)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_mod_passado"
        verbose_name = "Modelo de análise do passado"
        verbose_name_plural = "Modelos de análise do passado"


class ModeloPassadoPeriodo(models.Model):
    modelo = models.ForeignKey(
        ModeloPassado, on_delete=models.CASCADE)
    ordem = models.IntegerField()
    meses = models.IntegerField()
    peso = models.IntegerField()

    def __str__(self):
        return '{}, período #{} - {} {}; peso {}'.format(
            self.modelo.nome,
            self.ordem,
            self.meses,
            ('mês' if self.meses == 1 else 'meses'),
            self.peso,
        )

    class Meta:
        db_table = "fo2_mod_pass_periodo"
        verbose_name = "Período de modelo de análise do passado"
        verbose_name_plural = "Períodos de modelo de análise do passado"


class MetaModeloReferencia(models.Model):
    modelo = models.CharField(
        max_length=5,
    )
    referencia = models.CharField(
        max_length=5,
        verbose_name='Referência',
    )
    incl_excl = models.CharField(
        max_length=1,
        verbose_name='Inclui/Exclui',
    )

    def __str__(self):
        incl_excl = "Inclui" if self.incl_excl == 'i' else "Exclui"
        return f'{self.modelo} - {incl_excl} {self.referencia}'

    class Meta:
        db_table = "fo2_meta_mod_ref"
        verbose_name = "Referência de modelo para meta"
        verbose_name_plural = "Referências de modelos para meta"


class MetaEstoque(models.Model):
    modelo = models.CharField(max_length=5)
    data = models.DateField()
    venda_mensal = models.IntegerField()
    multiplicador = models.FloatField()
    meta_estoque = models.IntegerField(
        default=0)
    meta_giro = models.IntegerField(
        default=0)

    def __str__(self):
        return f'{self.modelo} - {self.data}'

    class Meta:
        db_table = "fo2_meta_estoque"
        verbose_name = "Parametros para meta de estoque"
        permissions = (("can_define_goal", "Can define goal"),
                       )


def getMetaEstoqueAtual():
    metas = MetaEstoque.objects
    metas = metas.annotate(antiga=Exists(
        MetaEstoque.objects.filter(
            modelo=OuterRef('modelo'),
            data__gt=OuterRef('data')
        )
    ))
    metas = metas.filter(antiga=False)
    return metas


class MetaEstoqueTamanho(models.Model):
    meta = models.ForeignKey(
        MetaEstoque, on_delete=models.CASCADE)
    tamanho = models.CharField(max_length=3)
    quantidade = models.IntegerField()
    ordem = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.meta.modelo} - {self.meta.data} - {self.tamanho}'

    class Meta:
        db_table = "fo2_meta_estoque_tamanho"
        verbose_name = "Grade de tamanhos de meta de estoque"


class MetaEstoqueCor(models.Model):
    meta = models.ForeignKey(
        MetaEstoque, on_delete=models.CASCADE)
    cor = models.CharField(max_length=6)
    quantidade = models.IntegerField()

    def __str__(self):
        return f'{self.meta.modelo} - {self.meta.data} - {self.cor}'

    class Meta:
        db_table = "fo2_meta_estoque_cor"
        verbose_name = "Grade de cores de meta de estoque"


class MetaFaturamento(models.Model):
    data = models.DateField()
    faturamento = models.IntegerField(default=0)
    # ajuste: adiciona ao valor que será compensado nos próximos meses
    ajuste = models.IntegerField(default=0)
    # reparo: adiciona ao valor da meta do mês
    reparo = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.data} - R$ {self.faturamento}'

    class Meta:
        db_table = "fo2_meta_faturamento"
        verbose_name = "Meta de faturamento"
        permissions = (("can_define_revenues", "Can define revenues"),)


class PendenciaFaturamento(models.Model):
    mes = models.DateField(verbose_name='mês')
    ordem = models.IntegerField(default=1)
    cliente = models.CharField(max_length=50)
    pendencia = models.CharField(max_length=500, verbose_name='pendência')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    entrega = models.CharField(max_length=50)
    responsavel = models.CharField(max_length=50, verbose_name='responsável')
    obs = models.CharField(
        null=True, blank=True, max_length=50, verbose_name='observação')

    def __str__(self):
        return f'{self.cliente} - {self.entrega}'

    class Meta:
        db_table = "fo2_pendencia_faturamento"
        verbose_name = "Pendência de faturamento"

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


class MetaEstoque(models.Model):
    modelo = models.CharField(max_length=5)
    data = models.DateField()
    venda_mensal = models.IntegerField()
    multiplicador = models.FloatField()

    def __str__(self):
        return '{} - {}'.format(
            self.modelo,
            self.data,
        )

    class Meta:
        db_table = "fo2_meta_estoque"
        verbose_name = "Parametros para meta de estoque"


class MetaEstoqueTamanho(models.Model):
    meta = models.ForeignKey(
        MetaEstoque, on_delete=models.CASCADE)
    tamanho = models.CharField(max_length=3)
    quantidade = models.IntegerField()

    def __str__(self):
        return '{} - {}'.format(
            self.modelo,
            self.data,
        )

    class Meta:
        db_table = "fo2_meta_estoque_tamanho"
        verbose_name = "Grade de tamanhos de meta de estoque"

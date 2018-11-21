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
    codigo = models.CharField(
        max_length=5, unique=True,
        verbose_name='Código identificador do range')

    def __str__(self):
        return '{} ({})'.format(self.codigo, self.ordem)

    class Meta:
        db_table = "fo2_gtin_range"
        verbose_name = "Range de GTIN"

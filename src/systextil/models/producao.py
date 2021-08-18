from django.db import models


class PeriodoConfeccaoManager(models.Manager):
    def get_queryset(self):
        return super(PeriodoConfeccaoManager, self).get_queryset().filter(
            area_periodo=1)


class Periodo(models.Model):
    area_periodo = models.IntegerField(
        verbose_name='Área do período')
    periodo_producao = models.IntegerField(
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

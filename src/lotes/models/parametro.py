from pprint import pprint

from django.db import models


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

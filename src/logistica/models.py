from django.db import models


class NotaFiscal(models.Model):
    numero = models.IntegerField(unique=True, verbose_name='número')
    ativa = models.BooleanField(default=True)
    faturamento = models.DateTimeField(null=True, blank=True)
    saida = models.DateField(null=True, blank=True, verbose_name='saída')
    entrega = models.DateField(
        null=True, blank=True, verbose_name='entrega/agendamento')
    confirmada = models.BooleanField(default=False)
    observacao = models.TextField(
        null=True, blank=True, verbose_name='observação')

    class Meta:
        db_table = "fo2_fat_nf"
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"

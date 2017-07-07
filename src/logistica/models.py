from django.db import models


class NotaFiscal(models.Model):
    numero = models.IntegerField(unique=True)
    ativa = models.BooleanField(default=True)
    saida = models.DateField(null=True, blank=True)
    entrega = models.DateField(null=True, blank=True)
    confirmada = models.BooleanField(default=False)
    observacao = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "fo2_fat_nf"

from django.db import models


class EstoqueManual(models.Model):
    data = models.DateField(
        db_index=True)
    referencia = models.CharField(
        db_index=True, max_length=5, verbose_name='Referência')
    tamanho = models.CharField(
        db_index=True, max_length=3)
    cor = models.CharField(
        db_index=True, max_length=6)
    qtd = models.IntegerField(
        default=0)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_estoque_manual"
        verbose_name = "Estoque manual de produtos acabados"

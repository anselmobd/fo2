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

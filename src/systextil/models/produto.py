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

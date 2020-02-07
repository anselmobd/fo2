from django.db import models


class Servidor(models.Model):
    descricao = models.CharField(
        unique=True, max_length=200,
        verbose_name='descrição',
        )
    hostname = models.CharField(
        unique=True, max_length=50,
        )
    ip4 = models.CharField(
        unique=True, max_length=15,
        )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = 'fo2_rfile_servidor'
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'

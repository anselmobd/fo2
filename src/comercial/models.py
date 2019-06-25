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

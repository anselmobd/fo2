from django.db import models


class TipoImagem(models.Model):
    codigo = models.IntegerField(db_index=True)
    descricao = models.CharField(
        max_length=50,
        verbose_name='Descrição',
        )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fo2_tipo_imagem"
        verbose_name = 'Tipo de imagem'
        verbose_name_plural = 'Tipos de imagem'

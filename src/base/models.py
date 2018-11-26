from django.db import models
from django.utils.text import slugify


class TipoImagem(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=10,
        )
    slug = models.SlugField()
    descricao = models.CharField(
        'Descrição',
        max_length=50,
        )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fo2_tipo_imagem"
        verbose_name = 'Tipo de imagem'
        verbose_name_plural = 'Tipos de imagem'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(TipoImagem, self).save(*args, **kwargs)

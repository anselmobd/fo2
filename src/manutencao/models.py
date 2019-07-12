from django.db import models
from django.utils.text import slugify


class TipoMaquina(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=20,
        )
    slug = models.SlugField()
    descricao = models.CharField(
        'Descrição',
        max_length=250,
        )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = 'fo2_man_tipo_maquina'
        verbose_name = 'Tipo de máquina'
        verbose_name_plural = 'Tipos de máquinas'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(TipoMaquina, self).save(*args, **kwargs)

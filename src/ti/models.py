from django.db import models
from django.template.defaultfilters import slugify


class TipoEquipamento(models.Model):
    name = models.CharField(
        'Nome', max_length=30, blank=False, null=False
    )
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(TipoEquipamento, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_tipo_equipamento"
        verbose_name = "Tipo de equipamento"
        verbose_name_plural = "Tipos de equipamentos"

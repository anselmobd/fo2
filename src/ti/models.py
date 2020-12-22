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


class Equipamento(models.Model):
    tipo = models.ForeignKey(
        TipoEquipamento, on_delete=models.PROTECT, blank=False, null=False
    )
    name = models.CharField(
        'Nome', max_length=50, blank=False, null=False,
    )
    slug = models.SlugField()
    ip = models.GenericIPAddressField(
        'IP', blank=True, null=True,
    )

    def __str__(self):
        return f"{self.tipo.name} - {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Equipamento, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_equipamento"



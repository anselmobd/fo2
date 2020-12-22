from django.db import models
from django.template.defaultfilters import slugify


class EquipmentType(models.Model):
    name = models.CharField(
        'Nome', max_length=30, blank=False, null=False
    )
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(EquipmentType, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_equipment_type"
        verbose_name = "Tipo de equipamento"
        verbose_name_plural = "Tipos de equipamentos"


class Equipment(models.Model):
    type = models.ForeignKey(
        EquipmentType, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Tipo'
    )
    name = models.CharField(
        'Nome', max_length=50, blank=False, null=False,
    )
    slug = models.SlugField()
    primary_ip = models.GenericIPAddressField(
        'IP Principal', blank=True, null=True,
    )

    def __str__(self):
        return f"{self.type.name} - {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Equipment, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_equipment"
        verbose_name = "Equipamento"


class TipoInterface(models.Model):
    name = models.CharField(
        'Nome', max_length=30, blank=False, null=False
    )
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(TipoInterface, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_interface_type"
        verbose_name = "Tipo de interface"
        verbose_name_plural = "Tipos de interfaces"


class Interface(models.Model):
    type = models.ForeignKey(
        TipoInterface, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Tipo'
    )
    name = models.CharField(
        'Nome', max_length=50, blank=False, null=False,
    )
    slug = models.SlugField()
    mac_adress = models.CharField(
        'Endereço MAC', max_length=17, blank=True, null=True,
    )
    ip = models.GenericIPAddressField(
        'IP', blank=True, null=True,
    )

    def __str__(self):
        return f"{self.type.name} - {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Interface, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_interface"

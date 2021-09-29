from django.db import models
from django.template.defaultfilters import slugify


class Empresa(models.Model):
    name = models.CharField(
        'Nome', max_length=20, blank=False, null=False
    )
    slug = models.SlugField(
        'Nome-chave', unique=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Empresa, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_empresa"
        verbose_name = "Empresa"


class OSType(models.Model):
    name = models.CharField(
        'Nome', max_length=60, blank=False, null=False
    )
    slug = models.SlugField(
        'Nome-chave', unique=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(OSType, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_os_type"
        verbose_name = "Tipo de SO"
        verbose_name_plural = "Tipos de SO"


class OS(models.Model):
    type = models.ForeignKey(
        OSType, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Tipo'
    )
    name = models.CharField(
        'Nome', max_length=60, blank=False, null=False
    )
    version = models.CharField(
        'Versão', max_length=60, blank=False, null=False
    )
    bits = models.IntegerField(
        blank=True, null=True,
    )
    slug = models.SlugField(
        'Nome-chave', unique=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        name_slug = slugify(self.name) 
        if self.type.slug != name_slug:
            name_slug = f"{self.type.slug}_{name_slug}"
        self.slug = f"{name_slug}_{slugify(self.version)}_{slugify(self.bits)}"
        super(OS, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_os"
        verbose_name = "SO"
        verbose_name_plural = "SO"


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
    slug = models.SlugField(
        'Nome-chave', unique=True
    )
    descr = models.CharField(
        'Descrição', max_length=200, blank=True, null=True,
    )
    use = models.CharField(
        'Uso', max_length=200, blank=True, null=True,
    )
    users = models.CharField(
        'Usuário(s)', max_length=100, blank=True, null=True,
    )
    primary_ip = models.GenericIPAddressField(
        'IP Principal', blank=True, null=True,
    )

    def __str__(self):
        return f"{self.type.name} - {self.name}"

    def save(self, *args, **kwargs):
        self.slug = f"{self.type.slug}_{slugify(self.name)}"
        super(Equipment, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_equipment"
        verbose_name = "Equipamento"


class InterfaceType(models.Model):
    name = models.CharField(
        'Nome', max_length=30, blank=False, null=False
    )
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(InterfaceType, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_interface_type"
        verbose_name = "Tipo de interface"
        verbose_name_plural = "Tipos de interfaces"


class DhcpConfig(models.Model):
    name = models.CharField(
        'Nome', max_length=50, blank=False, null=False
    )
    slug = models.SlugField()
    primary_equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Equipamento primário', related_name='primary_dhcp',
    )
    secondary_equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Equipamento secundário', related_name='secondary_dhcp',
    )
    primary_template = models.CharField(
        max_length=65535, blank=True, null=True,
        verbose_name='Gabarito para o servidor primário (ou único)'
    )
    secondary_template = models.CharField(
        max_length=65535, blank=True, null=True,
        verbose_name='Gabarito para o servidor secundário'
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(DhcpConfig, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_dhcp_config"
        verbose_name = "Configuração DHCP"
        verbose_name_plural = "Configurações DHCP"


class Interface(models.Model):
    """
        Cadastro de interface
        Obs.:
            - 'equipment': não é obrigatório pois pode ser, por exemplo um 
                adaptador de rede via USB
            - 'dhcp_config': quando presente é base para gerar entrada de
                configuração DHCP com o MAC e o IP da interface
    """
    type = models.ForeignKey(
        InterfaceType, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Tipo'
    )
    equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Equipamento'
    )
    name = models.CharField(
        'Nome', max_length=50, blank=False, null=False,
    )
    slug = models.SlugField()
    mac_adress = models.CharField(
        'Endereço MAC', max_length=17, blank=True, null=True,
    )
    fixed_ip = models.GenericIPAddressField(
        'IP', blank=True, null=True,
    )
    dhcp_config = models.ForeignKey(
        DhcpConfig, on_delete=models.PROTECT, blank=True, null=True,
        verbose_name='Configuração de DHCP'
    )

    def __str__(self):
        equip_name = f'{self.equipment.name} - ' if self.equipment else ''
        return f"{equip_name}{self.type.name} - {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Interface, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_interface"


class Share(models.Model):
    equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, blank=False, null=False,
        verbose_name='Servidor',
    )
    name = models.CharField(
        'Nome', max_length=30, blank=False, null=False
    )
    path = models.CharField(
        'Caminho', max_length=200, blank=False, null=False
    )
    read_only = models.BooleanField(
        'Somente leitura', default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Share, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ti_share"
        verbose_name = "Compartilhamento"

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


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
        return self.nome

    class Meta:
        db_table = 'fo2_man_tipo_maquina'
        verbose_name = 'Tipo de máquina'
        verbose_name_plural = 'Tipos de máquinas'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(TipoMaquina, self).save(*args, **kwargs)


class UnidadeTempo(models.Model):
    codigo = models.CharField(
        'Código',
        db_index=True,
        max_length=1,
        )
    nome = models.CharField(
        max_length=50,
        )

    def __str__(self):
        return '{}-{}'.format(self.codigo, self.nome)

    class Meta:
        db_table = 'fo2_man_unidade_tempo'
        verbose_name = 'Unidade de tempo'
        verbose_name_plural = 'Unidades de tempo'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(UnidadeTempo, self).save(*args, **kwargs)


class Maquina(models.Model):
    tipo_maquina = models.ForeignKey(
        TipoMaquina,
        verbose_name='Tipo de máquina',
        on_delete=models.CASCADE)
    nome = models.CharField(
        db_index=True,
        max_length=50,
        )
    slug = models.SlugField()
    descricao = models.CharField(
        "Descrição",
        max_length=250)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_man_maquina'
        verbose_name = 'Máquina'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(Maquina, self).save(*args, **kwargs)


class UsuarioTipoMaquina(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    tipo_maquina = models.ForeignKey(
        TipoMaquina, on_delete=models.CASCADE,
        verbose_name='Tipo de máquina')

    class Meta:
        db_table = "fo2_man_user_tipo_maq"
        verbose_name = "Usuário/Tipo de máquina"
        verbose_name_plural = "Usuários/Tipos de máquinas"
        unique_together = ("usuario", "tipo_maquina")

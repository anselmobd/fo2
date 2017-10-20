from django.db import models
from django.contrib.auth.models import User


class Impresso(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impresso"
        verbose_name = "Impresso"


class ModeloTermica(models.Model):
    codigo = models.CharField(
        unique=True, max_length=20, null=True, blank=True,
        verbose_name='código')
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='nome')
    modelo = models.TextField(
        null=True, blank=True,
        verbose_name='modelo')
    campos = models.TextField(
        null=True, blank=True,
        verbose_name='campos')

    def __str__(self):
        return self.codigo

    class Meta:
        db_table = "fo2_lot_modelo_termica"
        verbose_name = "modelo de etiqueta térmica"
        verbose_name_plural = "modelos de etiqueta térmica"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo and self.codigo.upper()
        super(ModeloTermica, self).save(*args, **kwargs)


class ImpressoraTermica(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impr_termica"
        verbose_name = "impressora térmica"
        verbose_name_plural = "impressoras térmicas"


class UsuarioImpresso(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    impresso = models.ForeignKey(
        Impresso, on_delete=models.CASCADE,
        verbose_name='impresso')
    impressora_termica = models.ForeignKey(
        ImpressoraTermica, on_delete=models.CASCADE,
        verbose_name='impressora térmica')
    modelo = models.ForeignKey(
        ModeloTermica, on_delete=models.CASCADE,
        verbose_name='modelo padrão')

    class Meta:
        db_table = "fo2_lot_usuario_impresso"
        verbose_name = "Impressos de usuário"
        verbose_name_plural = "Impressos de usuários"
        unique_together = ("usuario", "impresso")

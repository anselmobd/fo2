from django.db import models


class HDoc001(models.Model):
    tipo = models.IntegerField(
        primary_key=True)
    codigo = models.IntegerField(
        primary_key=True,
        verbose_name='Código')
    descricao = models.CharField(
        max_length=60,
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}-{}'.format(self.tipo, self.codigo, self.descricao)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "HDOC_001"
        verbose_name = "Tabela auxiliar HDOC_001"


class UsuarioManager(models.Manager):
    def get_queryset(self):
        return super(
            UsuarioManager,
            self).get_queryset().filter(ativo_inativo=1)


class Usuario(models.Model):
    usuario = models.CharField(
        primary_key=True,
        max_length=15,
        verbose_name='Usuário')
    codigo_usuario = models.IntegerField(
        verbose_name='Código do Usuário')
    ativo_inativo = models.IntegerField(
        verbose_name='Ativo ou inativo')

    objects = UsuarioManager()

    def __str__(self):
        return f'{self.usuario} ({self.codigo_usuario})'

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "HDOC_030"
        verbose_name = "Usuário"

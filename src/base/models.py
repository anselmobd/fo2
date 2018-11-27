import os

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


def upload_to(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return "upload/imagens/{tipo_imagem}/{filename}{extension}".format(
        tipo_imagem=instance.tipo_imagem.slug,
        filename=instance.slug,
        extension=filename_ext.lower(),
    )


class Imagem(models.Model):
    tipo_imagem = models.ForeignKey(
        TipoImagem,
        verbose_name='Tipo da imagem',
        on_delete=models.CASCADE)
    descricao = models.CharField(
        "Descrição",
        max_length=255)
    slug = models.SlugField()
    imagem = models.ImageField(
        upload_to=upload_to)

    def __str__(self):
        return '({}) {}'.format(self.tipo_imagem.nome, self.descricao)

    class Meta:
        db_table = "fo2_imagem"
        verbose_name = "Imagem"
        verbose_name_plural = "Imagens"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.descricao)
        super(Imagem, self).save(*args, **kwargs)


class ImagemTagManager(models.Manager):
    def get_queryset(self):
        return super(ImagemTagManager, self).get_queryset().filter(
            tipo_imagem__nome='TAG')


class ImagemTag(Imagem):
    objects = ImagemTagManager()

    class Meta:
        proxy = True
        verbose_name = "Imagem para TAG"
        verbose_name_plural = "Imagens para TAG"

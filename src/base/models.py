import os

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Colaborador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
        verbose_name='usuário')
    matricula = models.CharField(
        max_length=5, unique=True, default='00000',
        verbose_name='matrícula')
    nome = models.CharField(
        null=True, blank=True, max_length=100)
    nascimento = models.DateField(
        null=True, blank=True)
    cpf = models.CharField(
        max_length=11, unique=True, default=0,
        verbose_name='CPF')
    obs = models.CharField(
        null=True, blank=True, max_length=1000)
    logged = models.BooleanField(
        default=False)
    quando = models.DateTimeField(
        null=True, blank=True)
    ip_interno = models.BooleanField(
        default=False)

    def __str__(self):
        return f"{self.user} ({self.matricula}) {self.nome}"

    class Meta:
        db_table = "fo2_colaborador"
        verbose_name_plural = 'Colaboradores'
        permissions = (
            ("can_generate_product_stages", "Can generate product stages"),
            ("can_adjust_stock", "Can adjust stock"),
        )


class Requisicao(models.Model):
    colaborador = models.ForeignKey(Colaborador, on_delete=models.PROTECT)
    request_method = models.CharField(
        max_length=10, verbose_name='Tipo de requisição')
    path_info = models.CharField(
        max_length=254, verbose_name='Endereço')
    http_accept = models.CharField(
        max_length=254, verbose_name='HTTP Accept')
    quando = models.DateTimeField(
        null=True, blank=True)
    ip = models.CharField(
        max_length=47, verbose_name='IP')

    def __str__(self):
        return f"{self.colaborador.user.username} - {self.quando}"

    class Meta:
        db_table = "fo2_requisicao"
        verbose_name = 'Requisição'
        verbose_name_plural = 'Requisições'
        permissions = (
            ("can_visualize_usage_log", "Can visualize usage log"),
        )

    def save(self, *args, **kwargs):
        self.request_method = self.request_method[:10]
        self.path_info = self.path_info[:254]
        self.http_accept = self.http_accept[:254]
        self.ip = self.ip[:47]
        super(Requisicao, self).save(*args, **kwargs)


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
    _, filename_ext = os.path.splitext(filename)
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


class Tamanho(models.Model):
    nome = models.CharField(max_length=3)
    ordem = models.IntegerField()

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_tamanho"
        verbose_name = "Tamanho"


class SyncDelTable(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_sync_del_table"
        verbose_name = "Sincronização de deleção - Tabela"


class SyncDel(models.Model):
    tabela = models.ForeignKey(SyncDelTable, on_delete=models.PROTECT)
    sync_id = models.IntegerField()

    def __str__(self):
        return f'{self.tabela__nome}#{self.sync_id}'

    class Meta:
        db_table = "fo2_sync_del"
        verbose_name = "Sincronização de deleção"

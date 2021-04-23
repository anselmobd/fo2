from pprint import pprint

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User

from utils.classes import LoggedInUser


class EquipeAtendimento(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=20,
    )
    slug = models.SlugField()
    descricao = models.CharField(
        'Descrição',
        max_length=250,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_serv_equipe'
        verbose_name = 'Equipe de atendimento'
        verbose_name_plural = 'Equipes de atendimento'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        if not self.descricao:
            self.descricao = self.nome
        super(EquipeAtendimento, self).save(*args, **kwargs)


class TipoFuncaoExercida(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=20,
    )
    slug = models.SlugField()
    # nivel_operacional:
    # -5: diretor
    # -4: gerente
    # -3: chefe
    # -2: usuário
    # -1: auxiliar
    # 1: auxiliar
    # 2: executor
    # 3: chefe
    # 4: supervisor
    # 5: supervisor geral
    nivel_operacional = models.IntegerField(
        'Nível operacional',
        default=0,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_serv_tp_funcao_exer'
        verbose_name = 'Tipo de função exercida'
        verbose_name_plural = 'Tipos de função exercida'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(TipoFuncaoExercida, self).save(*args, **kwargs)


class PapelUsuario(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='usuário')
    funcao = models.ForeignKey(
        TipoFuncaoExercida, on_delete=models.PROTECT,
        verbose_name='função')
    equipe = models.ForeignKey(
        EquipeAtendimento, on_delete=models.PROTECT,
        null=True, blank=True,
        )

    def __str__(self):
        equipe = f" {self.equipe}" if self.equipe else ""
        return f"{self.usuario} ({self.funcao}){equipe}"

    class Meta:
        db_table = "fo2_serv_papel_usuario"
        verbose_name = "Papel de usuário"
        verbose_name_plural = "Papeis de usuário"


class NivelAtendimento(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=20,
    )
    slug = models.SlugField()
    horas = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_serv_nivel_atend'
        verbose_name = 'Nível de atendimento'
        verbose_name_plural = 'Níveis de atendimento'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(NivelAtendimento, self).save(*args, **kwargs)


class TipoDocumento(models.Model):
    nome = models.CharField(
        max_length=20,
    )
    slug = models.SlugField()

    def __str__(self):
        return f"{self.nome} ({self.slug})"

    class Meta:
        db_table = 'fo2_serv_tipo_doc'
        verbose_name = 'Tipo de documento'
        verbose_name_plural = 'Tipos de documento'


class Status(models.Model):
    nome = models.CharField(
        max_length=20,
    )
    codigo = models.CharField(
        max_length=20,
    )

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    class Meta:
        db_table = 'fo2_serv_status'
        verbose_name = 'Status'
        verbose_name_plural = verbose_name


class Documento(models.Model):
    tipo = models.ForeignKey(
        TipoDocumento, on_delete=models.PROTECT,
    )
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='criado em',
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        blank=True,
        verbose_name='usuário',
    )
    ativo = models.BooleanField(
        default=False,
    )
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT,
        # default=Status.objects.get(criado=True).id
    )

    @property
    def numero(self):
        return self.id

    def __str__(self):
        return f"{self.tipo} {self.id}"

    class Meta:
        db_table = 'fo2_serv_doc'
        verbose_name = 'Documento'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
            self.status = StatusEvento.objects.get(status_pre=None).status_pos
        logged_in = LoggedInUser()
        self.user = logged_in.user
        super(Documento, self).save(*args, **kwargs)


class Evento(models.Model):
    nome = models.CharField(
        max_length=20,
    )
    codigo = models.CharField(
        max_length=20,
    )
    ordem = models.IntegerField(
        default=0,
    )
    edita_nivel = models.BooleanField(
        default=False,
    )
    edita_equipe = models.BooleanField(
        default=False,
    )
    edita_descricao = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_serv_evento'
        verbose_name = 'Evento'


class StatusEvento(models.Model):
    status_pre = models.ForeignKey(
        Status, on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='eventos_dependentes'
    )
    evento = models.ForeignKey(
        Evento, on_delete=models.PROTECT,
    )
    status_pos = models.ForeignKey(
        Status, on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='eventos_criadores'
    )

    class Meta:
        db_table = 'fo2_serv_status_evento'
        verbose_name = 'Status-Evento'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.status_pre and not self.status_pos:
            raise ValidationError(f"Ao menos um status deve ser indicado.")
        super(StatusEvento, self).save(*args, **kwargs)


class ServicoEvento(models.Model):
    numero = models.ForeignKey(
        Documento, on_delete=models.PROTECT,
        verbose_name='Número',
    )
    evento = models.ForeignKey(
        Evento, on_delete=models.PROTECT,
    )
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Criado em',
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        blank=True,
        verbose_name='Usuário',
    )
    nivel = models.ForeignKey(
        NivelAtendimento, on_delete=models.PROTECT,
        verbose_name='Nível de atendimento',
    )
    equipe = models.ForeignKey(
        EquipeAtendimento, on_delete=models.PROTECT,
        verbose_name='Equipe de atendimento',
    )
    descricao = models.TextField(
        'Descrição',
        max_length=2000,
        default='',
    )

    class Meta:
        db_table = 'fo2_serv_servico_evento'
        verbose_name = 'Evento relacionado a serviços'
        verbose_name_plural = 'Eventos relacionados a serviços'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
        logged_in = LoggedInUser()
        self.user = logged_in.user
        super(ServicoEvento, self).save(*args, **kwargs)

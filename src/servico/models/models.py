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


class FuncaoExercida(models.Model):
    nome = models.CharField(
        db_index=True,
        max_length=20,
    )
    slug = models.SlugField()
    # nivel_operacional:
    #     cliente do serviço
    # -5: diretor
    # -4: gerente
    # -3: chefe
    # -2: usuário
    # -1: auxiliar
    # 0: visitante
    # 1: auxiliar
    # 2: executor
    # 3: chefe
    # 4: supervisor
    # 5: supervisor geral
    #     responsável pelo serviço
    nivel_operacional = models.IntegerField(
        'Nível operacional',
        default=0,
    )
    parte = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_serv_funcao_exercida'
        verbose_name = 'Função exercida'
        verbose_name_plural = 'Funções exercidas'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(FuncaoExercida, self).save(*args, **kwargs)


class UsuarioFuncao(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='usuário')
    funcao = models.ForeignKey(
        FuncaoExercida, on_delete=models.PROTECT,
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
        verbose_name = "Usuário-função"
        verbose_name_plural = "Usuários-funções"


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
        return f"{self.nome}"

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

    def __str__(self):
        return f"{self.tipo} {self.id}"

    class Meta:
        db_table = 'fo2_serv_doc'
        verbose_name = 'Documento'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
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

    def __str__(self):
        status_pre = self.status_pre if self.status_pre else '{}'
        status_pos = self.status_pos if self.status_pos else '{}'
        return f"{status_pre} >--({self.evento})--> {status_pos}"

    class Meta:
        db_table = 'fo2_serv_status_evento'
        verbose_name = 'Status-Evento'
        verbose_name_plural = 'Status-Eventos'

    def save(self, *args, **kwargs):
        if not self.status_pre and not self.status_pos:
            raise ValidationError(f"Ao menos um status deve ser indicado.")
        if not self.status_pre:
            try:
                StatusEvento.objects.get(status_pre=None)
                raise ValidationError(f"Apenas um StatusEvento pode ter o campo status_pre nulo.")
            except StatusEvento.DoesNotExist:
                pass
        super(StatusEvento, self).save(*args, **kwargs)


class Interacao(models.Model):
    documento = models.ForeignKey(
        Documento, on_delete=models.PROTECT,
    )
    evento = models.ForeignKey(
        Evento, on_delete=models.PROTECT,
    )
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT,
        default=1,
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
        db_table = 'fo2_serv_interacao'
        verbose_name = 'Interação em documento'
        verbose_name_plural = 'Interações em documentos'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
        logged_in = LoggedInUser()
        self.user = logged_in.user
        super(Interacao, self).save(*args, **kwargs)

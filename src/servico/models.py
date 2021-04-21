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


class StatusDocumento(models.Model):
    nome = models.CharField(
        max_length=20,
    )
    slug = models.SlugField()
    criado = models.BooleanField(
        default=False,
    )
    cancelado = models.BooleanField(
        default=False,
    )
    iniciado = models.BooleanField(
        default=False,
    )
    terminado = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.nome} ({self.slug})"

    class Meta:
        db_table = 'fo2_serv_status_doc'
        verbose_name = 'Status de documento'
        verbose_name_plural = verbose_name

    def so1(self, field, name):
        if self.__dict__[field]:
            filtro = {field: True}
            evento = StatusDocumento.objects.filter(**filtro)
            if self.id:
                evento = evento.exclude(id=self.id)
            if evento.count() != 0:
                raise ValidationError(f"Só pode haver um status de {name}.")

    def save(self, *args, **kwargs):
        self.so1('criado', 'criação')
        self.so1('cancelado', 'inativação')
        self.so1('iniciado', 'ativação')
        self.so1('terminado', 'ativação')
        super(StatusDocumento, self).save(*args, **kwargs)


class NumeroDocumento(models.Model):
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
        StatusDocumento, on_delete=models.PROTECT,
        default=StatusDocumento.objects.get(criado=True).id
    )

    def __str__(self):
        return f"{self.tipo} {self.id}"

    class Meta:
        db_table = 'fo2_serv_num_doc'
        verbose_name = 'Número de documento'
        verbose_name_plural = 'Números de documento'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
            self.status = StatusDocumento.objects.get(criado=True)
        logged_in = LoggedInUser()
        self.user = logged_in.user
        super(NumeroDocumento, self).save(*args, **kwargs)


class TipoEvento(models.Model):
    nome = models.CharField(
        max_length=20,
    )
    slug = models.SlugField()
    ordem = models.IntegerField(
        default=0,
    )
    criar = models.BooleanField(
        default=False,
    )
    inativar = models.BooleanField(
        default=False,
    )
    ativar = models.BooleanField(
        default=False,
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
        db_table = 'fo2_serv_tipo_evento'
        verbose_name = 'Tipo de evento'
        verbose_name_plural = 'Tipos de evento'

    def so1(self, field, name):
        if self.__dict__[field]:
            filtro = {field: True}
            evento = TipoEvento.objects.filter(**filtro)
            if self.id:
                evento = evento.exclude(id=self.id)
            if evento.count() != 0:
                raise ValidationError(f"Só pode haver um evento de {name}.")

    def save(self, *args, **kwargs):
        self.so1('criar', 'criação')
        self.so1('inativar', 'inativação')
        self.so1('ativar', 'ativação')
        super(TipoEvento, self).save(*args, **kwargs)


class EventoDeStatus(models.Model):
    status = models.ForeignKey(
        StatusDocumento, on_delete=models.PROTECT,
    )
    evento = models.ForeignKey(
        TipoEvento, on_delete=models.PROTECT,
    )

    class Meta:
        db_table = 'fo2_serv_evento_status'
        verbose_name = 'Evento de status'
        verbose_name_plural = 'Eventos de status'


class ServicoEvento(models.Model):
    numero = models.ForeignKey(
        NumeroDocumento, on_delete=models.PROTECT,
        verbose_name='Número',
    )
    evento = models.ForeignKey(
        TipoEvento, on_delete=models.PROTECT,
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

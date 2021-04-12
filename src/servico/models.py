from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User


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

    class Meta:
        db_table = 'fo2_serv_tipo_doc'
        verbose_name = 'Tipo de documento'
        verbose_name_plural = 'Tipos de documento'


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
        verbose_name='usuário',
    )
    ativo = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = 'fo2_serv_num_doc'
        verbose_name = 'Número de documento'
        verbose_name_plural = 'Números de documento'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
        super(NumeroDocumento, self).save(*args, **kwargs)

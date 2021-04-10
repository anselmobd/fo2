from django.db import models
from django.utils.text import slugify


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
    # -1: local
    # 1: auxilia
    # 2: executa
    # 3: chefia
    # 4: supervisiona
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



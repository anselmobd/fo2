from pprint import pprint

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

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
        return self.slug

    class Meta:
        db_table = 'fo2_man_tipo_maquina'
        verbose_name = 'Tipo de máquina'
        verbose_name_plural = 'Tipos de máquinas'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(TipoMaquina, self).save(*args, **kwargs)


class SubtipoMaquina(models.Model):
    tipo_maquina = models.ForeignKey(
        TipoMaquina,
        verbose_name='Tipo de máquina',
        on_delete=models.PROTECT,
    )
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
        return f"{self.tipo_maquina.slug}.{self.slug}"

    class Meta:
        db_table = 'fo2_man_subtipo_maquina'
        verbose_name = 'Subtipo de máquina'
        verbose_name_plural = 'Subtipos de máquinas'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(SubtipoMaquina, self).save(*args, **kwargs)


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


class Frequencia(models.Model):
    nome = models.CharField(
        max_length=50,
    )
    unidade_tempo = models.ForeignKey(
        UnidadeTempo,
        verbose_name='Unidade de tempo',
        on_delete=models.PROTECT,
    )
    qtd_tempo = models.IntegerField(
        'Quantidade de tempo',
        default=1,
    )
    ordem = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_man_frequencia'
        verbose_name = 'Frequência'


class Maquina(models.Model):
    tipo_maquina = models.ForeignKey(
        TipoMaquina,
        verbose_name='Tipo de máquina',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    subtipo_maquina = models.ForeignKey(
        SubtipoMaquina,
        verbose_name='Subtipo de máquina',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    nome = models.CharField(
        db_index=True,
    max_length=50,
    )
    slug = models.SlugField()
    descricao = models.CharField(
        "Descrição",
        max_length=250,
    )
    data_inicio = models.DateField(
        "Data de início da rotina",
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'fo2_man_maquina'
        verbose_name = 'Máquina'
        constraints = [
            models.CheckConstraint(
                check=Q(tipo_maquina__isnull=False) | Q(subtipo_maquina__isnull=False),
                name='not_both_null'
            ),
            models.CheckConstraint(
                check=Q(tipo_maquina__isnull=True) | Q(subtipo_maquina__isnull=True),
                name='not_both_not_null'
            )
        ]
    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        # pprint([self.tipo_maquina, self.subtipo_maquina])
        # pprint(map(lambda x: x is None, [self.tipo_maquina, self.subtipo_maquina]))
        # pprint(list(map(lambda x: x is None, [self.tipo_maquina, self.subtipo_maquina])))
        # if sum(map(lambda x: x is None, [self.tipo_maquina, self.subtipo_maquina])) != 1:
        #     raise ValidationError('Tipo ou Subtipo deve ser definido')
        super(Maquina, self).save(*args, **kwargs)


class UsuarioTipoMaquina(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='usuário',
    )
    tipo_maquina = models.ForeignKey(
        TipoMaquina,
        on_delete=models.PROTECT,
        verbose_name='Tipo de máquina',
    )

    class Meta:
        db_table = "fo2_man_user_tipo_maq"
        verbose_name = "Usuário/Tipo de máquina"
        verbose_name_plural = "Usuários/Tipos de máquinas"
        unique_together = ("usuario", "tipo_maquina")


class Atividade(models.Model):
    resumo = models.CharField(
        db_index=True,
        max_length=100,
    )
    descricao = models.CharField(
        'Descrição',
        max_length=400,
    )

    def __str__(self):
        return '{}-{}'.format(self.id, self.resumo)

    class Meta:
        db_table = 'fo2_man_atividade'
        verbose_name = 'Atividade'


class AtividadeMetrica(models.Model):
    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.PROTECT,
    )
    ordem = models.IntegerField(
        default=0,
    )
    descricao = models.CharField(
        'Descrição',
        max_length=50,
    )

    def __str__(self):
        return '{}: {} - {}'.format(
            self.atividade.resumo, self.ordem, self.descricao)

    class Meta:
        db_table = 'fo2_man_atividade_metrica'
        verbose_name = 'Metrica de atividade'
        verbose_name_plural = "Metricas de atividades"


class Rotina(models.Model):
    tipo_maquina = models.ForeignKey(
        TipoMaquina,
        verbose_name='Tipo de máquina',
        on_delete=models.PROTECT,
    )
    frequencia = models.ForeignKey(
        Frequencia,
        default=1,
        verbose_name='Período',
        on_delete=models.PROTECT,
    )
    nome = models.CharField(
        max_length=50,
    )

    def __str__(self):
        return '{} - {} - {}'.format(
            self.tipo_maquina.nome, self.frequencia.nome, self.nome)

    class Meta:
        db_table = 'fo2_man_rotina'
        verbose_name = 'Rotina de manutenção'
        verbose_name_plural = "Rotinas de manutenção"


class RotinaPasso(models.Model):
    rotina = models.ForeignKey(
        Rotina,
        on_delete=models.PROTECT,
    )
    ordem = models.IntegerField(
        default=0,
    )
    atividade = models.ForeignKey(
        Atividade,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return '{} : {:02} : {}'.format(
            self.rotina, self.ordem, self.atividade)

    class Meta:
        db_table = 'fo2_man_rotina_passo'
        verbose_name = 'Passo de rotina de manutenção'
        verbose_name_plural = "Passos de rotinas de manutenção"


class OS(models.Model):
    numero = models.IntegerField(
        default=0,
        verbose_name='número',
    )
    maquina = models.ForeignKey(
        Maquina,
        on_delete=models.PROTECT,
        verbose_name='máquina',
    )
    rotina = models.ForeignKey(
        Rotina,
        on_delete=models.PROTECT,
    )
    data_agendada = models.DateField(
        "Data agendada",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='usuário',
    )

    def __str__(self):
        return '{} : {:02} : {}'.format(
            self.rotina, self.ordem, self.atividade)

    class Meta:
        db_table = 'fo2_man_os'
        verbose_name = 'OS de rotina de manutenção'
        verbose_name_plural = "OSs de rotinas de manutenção"

    def save(self, *args, **kwargs):
        max_os = OS.objects.all().order_by('-numero').first()
        if max_os is None:
            numero = 1001
        else:
            numero = max_os.numero + 1
        self.numero = numero
        super(OS, self).save(*args, **kwargs)

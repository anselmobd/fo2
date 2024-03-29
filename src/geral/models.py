import os

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from base.models import Empresa

__all__ = [
    'ProxyUser',
    'RecordTracking',
    'Dispositivos',
    'RoloBipado',
    'Painel',
    'PainelModulo',
    'UsuarioPainelModulo',
    'InformacaoModulo',
    'PopGrupoAssunto',
    'PopAssunto',
    'Pop',
    'UsuarioPopAssunto',
    'TipoParametro',
    'Parametro',
    'Config',
    'TipoMaquina',
]


class ProxyUser(User):

    class Meta:
        proxy = True
        verbose_name = f"(Proxy) {User._meta.verbose_name}"
        verbose_name_plural = f"(Proxy) {User._meta.verbose_name_plural}"


class RecordTracking(models.Model):
    user = models.CharField(
        null=True, blank=True,
        max_length=64, verbose_name='Usuário')
    time = models.DateTimeField(
        null=True, blank=True,
        auto_now_add=True, verbose_name='Hora')
    table = models.CharField(
        max_length=64, verbose_name='Tabela')
    record_id = models.IntegerField(
        db_index=True, verbose_name='Id do registro')
    iud = models.CharField(
        max_length=1, verbose_name='Ação')
    # versão 1
    #   rt.log = dict_object
    # versão 2
    #   rt.log = yaml
    log_version = models.SmallIntegerField(
        verbose_name='Versão do log', default=1)
    log = models.CharField(
        max_length=65535, verbose_name='Log')

    class Meta:
        db_table = "fo2_ger_record_tracking"
        verbose_name = "log de registro"
        verbose_name_plural = "logs de registro de tabela"
        index_together = [
            ("time", "table", "record_id"),
        ]
        indexes = [
            models.Index(fields=['-id'], name='fo2_ger_record_track_desc_id'),
        ]


class Dispositivos(models.Model):
    key = models.CharField(
        max_length=64, verbose_name='Chave de identificação')
    nome = models.CharField(
        null=True, blank=True,
        max_length=64, verbose_name='Nome do dispositivo')

    def __str__(self):
        if self.nome:
            return self.nome
        else:
            return self.key

    class Meta:
        db_table = "fo2_ger_dispositivos"
        verbose_name = "dispositivo"


class RoloBipado(models.Model):
    dispositivo = models.ForeignKey(
        Dispositivos, on_delete=models.PROTECT, null=True, blank=True)
    rolo = models.IntegerField(
        verbose_name='Rolo')
    date = models.DateTimeField(
        auto_now_add=True, blank=True, verbose_name='Data/Hora')
    referencia = models.CharField(
        max_length=5, verbose_name='Referência')
    tamanho = models.CharField(
        max_length=3, verbose_name='Tamanho')
    cor = models.CharField(
        max_length=6, verbose_name='Cor')
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name='usuário')

    class Meta:
        db_table = "fo2_ger_rolo_bipado"
        verbose_name = "rolo bipado"
        verbose_name_plural = "rolos bipados"
        permissions = (("can_beep_rolo", "Can beep rolo"),)


class Painel(models.Model):
    # empresa = models.ForeignKey(
    #     Empresa,
    #     on_delete=models.PROTECT
    # )
    # empresa = models.IntegerField()
    nome = models.CharField(
        null=True, blank=True,
        max_length=64)
    slug = models.SlugField()
    layout = models.CharField(
        null=True, blank=True, max_length=4096,
        verbose_name='receita')
    habilitado = models.BooleanField(
        default=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_ger_painel"
        verbose_name = "painel"
        verbose_name_plural = "paineis"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(Painel, self).save(*args, **kwargs)


class PainelModulo(models.Model):
    nome = models.CharField(
        null=True, blank=True,
        max_length=64)
    slug = models.SlugField()
    TIPOS_DE_MODULOS = (
        ('I', 'Informativo'),
        ('C', 'URL de cartaz em imagem'),
    )
    tipo = models.CharField(
        max_length=1, choices=TIPOS_DE_MODULOS,
        default='I')
    habilitado = models.BooleanField(
        default=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_ger_painel_modulo"
        verbose_name = "modulo de painel"
        verbose_name_plural = "modulos de painel"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(PainelModulo, self).save(*args, **kwargs)


class UsuarioPainelModulo(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='usuário')
    painel_modulo = models.ForeignKey(
        PainelModulo, on_delete=models.PROTECT,
        verbose_name='módulo de painel')

    def __str__(self):
        return f"{self.usuario} -> {self.painel_modulo}"

    class Meta:
        db_table = "fo2_ger_usr_pnl_modulo"
        verbose_name = "usuário de modulo de painel"
        verbose_name_plural = "usuários de modulos de painel"


class InformacaoModulo(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='usuário')
    painel_modulo = models.ForeignKey(
        PainelModulo, on_delete=models.PROTECT,
        verbose_name='módulo de painel')
    data = models.DateTimeField(
        null=True, blank=True,
        auto_now_add=True, verbose_name='Data')
    chamada = models.CharField(
        max_length=400, null=True, blank=True,
        verbose_name='chamada')
    habilitado = models.BooleanField(
        default=True)
    texto = models.CharField(
        null=True, blank=True, max_length=4096,
        verbose_name='receita')

    class Meta:
        db_table = "fo2_ger_modulo_info"


class PopGrupoAssunto(models.Model):
    nome = models.CharField(
        max_length=255, blank=True)
    slug = models.SlugField(default='slug')
    ordem = models.IntegerField(
        default=0)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(PopGrupoAssunto, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ger_pop_grup_assu"


class PopAssunto(models.Model):
    nome = models.CharField(
        max_length=255, blank=True)
    slug = models.SlugField(default='slug')
    grupo_assunto = models.ForeignKey(
        PopGrupoAssunto,
        on_delete=models.PROTECT,
        default=1,
    )
    diretorio = models.CharField(
        'diretório',
        max_length=50, blank=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        self.grupo_slug = slugify(self.grupo)
        super(PopAssunto, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_ger_pop_assunto"


def pop_upload_to(instance, filename):
    return os.path.join('pop', instance.assunto.diretorio, filename)


class Pop(models.Model):
    assunto = models.ForeignKey(
        PopAssunto, on_delete=models.PROTECT, default=1,
        verbose_name='assunto do POP')
    descricao = models.CharField(
        max_length=255, blank=True, verbose_name='título')
    topico = models.CharField(
        max_length=255, blank=True, verbose_name='tópico')
    pop = models.FileField(upload_to=pop_upload_to, verbose_name='Arquivo POP')
    uploaded_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Inserido em')
    habilitado = models.BooleanField(
        default=True)

    class Meta:
        db_table = "fo2_ger_pop"
        permissions = (("can_manage_pop", "Can manage pop"),)


class UsuarioPopAssunto(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT,
        verbose_name='usuário')
    assunto = models.ForeignKey(
        PopAssunto, on_delete=models.PROTECT,
        verbose_name='assunto de POP')

    def __str__(self):
        return f"{self.usuario} - {self.assunto}"

    class Meta:
        db_table = "fo2_ger_usr_pop_assunto"
        verbose_name = "usuário de assunto de POP"
        verbose_name_plural = "usuários de assuntos de POPs"


class TipoParametro(models.Model):
    codigo = models.CharField(
        max_length=5, unique=True, verbose_name='código')

    descricao = models.CharField(
        max_length=255, unique=True, verbose_name='descrição')

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.descricao)

    class Meta:
        db_table = "fo2_param_tipo"
        verbose_name = "Tipo de parâmetro"
        verbose_name_plural = "Tipos de parâmetros"


class Parametro(models.Model):
    codigo = models.CharField(
        max_length=25, unique=True, verbose_name='código')

    descricao = models.CharField(
        max_length=255, unique=True, verbose_name='descrição')

    tipo = models.ForeignKey(
        TipoParametro, on_delete=models.PROTECT)

    ajuda = models.CharField(
        max_length=65535, null=True, blank=True)

    habilitado = models.BooleanField(
        default=True)

    usuario = models.BooleanField(
        default=True, verbose_name='usuário')

    def __str__(self):
        return '({}) {}'.format(self.codigo, self.descricao)

    class Meta:
        db_table = "fo2_parametro"
        verbose_name = "Parâmetro"


class Config(models.Model):
    parametro = models.ForeignKey(
        Parametro, on_delete=models.PROTECT)

    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name='usuário')

    valor = models.CharField(
        max_length=255)

    class Meta:
        db_table = "fo2_config"
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"


class TipoMaquina(models.Model):
    descricao = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='descrição',
    )

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fo2_maquina_tipo"
        verbose_name = "Tipo de máquina"
        verbose_name_plural = "Tipos de máquinas"

import os

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


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
    log = models.CharField(
        max_length=65535, verbose_name='Log')

    class Meta:
        db_table = "fo2_ger_record_tracking"
        verbose_name = "log de registro"
        verbose_name_plural = "logs de registro de tabela"


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
        Dispositivos, on_delete=models.CASCADE, null=True, blank=True)
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
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='usuário')

    class Meta:
        db_table = "fo2_ger_rolo_bipado"
        verbose_name = "rolo bipado"
        verbose_name_plural = "rolos bipados"
        permissions = (("can_beep_rolo", "Can beep rolo"),)


class Painel(models.Model):
    nome = models.CharField(
        null=True, blank=True,
        max_length=64)
    slug = models.SlugField()
    layout = models.CharField(
        null=True, blank=True, max_length=4096,
        verbose_name='receita')
    habilitado = models.NullBooleanField(
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
    habilitado = models.NullBooleanField(
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
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    painel_modulo = models.ForeignKey(
        PainelModulo, on_delete=models.CASCADE,
        verbose_name='módulo de painel')

    class Meta:
        db_table = "fo2_ger_usr_pnl_modulo"
        verbose_name = "usuário de modulo de painel"
        verbose_name_plural = "usuários de modulos de painel"


class InformacaoModulo(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    painel_modulo = models.ForeignKey(
        PainelModulo, on_delete=models.CASCADE,
        verbose_name='módulo de painel')
    data = models.DateTimeField(
        null=True, blank=True,
        auto_now_add=True, verbose_name='Data')
    chamada = models.CharField(
        max_length=200, null=True, blank=True,
        verbose_name='chamada')
    habilitado = models.NullBooleanField(default=True)
    texto = models.CharField(
        null=True, blank=True, max_length=4096,
        verbose_name='receita')

    class Meta:
        db_table = "fo2_ger_modulo_info"


class PopAssunto(models.Model):
    nome = models.CharField(
        max_length=255, blank=True)
    slug = models.SlugField(default='slug')
    grupo = models.CharField(
        max_length=255, blank=True)
    grupo_slug = models.SlugField(default='slug')
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
        PopAssunto, on_delete=models.CASCADE, default=1,
        verbose_name='assunto do POP')
    descricao = models.CharField(
        max_length=255, blank=True, verbose_name='título')
    pop = models.FileField(upload_to=pop_upload_to, verbose_name='Arquivo POP')
    uploaded_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Inserido em')
    habilitado = models.NullBooleanField(default=True)

    class Meta:
        db_table = "fo2_ger_pop"
        permissions = (("can_manage_pop", "Can manage pop"),)


class UsuarioPopAssunto(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    assunto = models.ForeignKey(
        PopAssunto, on_delete=models.CASCADE,
        verbose_name='assunto de POP')

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
        TipoParametro, on_delete=models.CASCADE)

    ajuda = models.CharField(
        max_length=65535, null=True, blank=True)

    habilitado = models.NullBooleanField(
        default=True)

    usuario = models.NullBooleanField(
        default=True, verbose_name='usuário')

    def __str__(self):
        return '({}) {}'.format(self.codigo, self.descricao)

    class Meta:
        db_table = "fo2_parametro"
        verbose_name = "Parâmetro"


class Config(models.Model):
    parametro = models.ForeignKey(
        Parametro, on_delete=models.CASCADE)

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='usuário')

    valor = models.CharField(
        max_length=255)

    class Meta:
        db_table = "fo2_config"
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"

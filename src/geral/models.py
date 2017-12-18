from django.db import models
from django.contrib.auth.models import User


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
        verbose_name='Id do registro')
    iud = models.CharField(
        max_length=1, verbose_name='Ação')
    log = models.CharField(
        max_length=2048, verbose_name='Log')

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
    dispositivo = models.ForeignKey(Dispositivos, on_delete=models.CASCADE)
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

    class Meta:
        db_table = "fo2_ger_rolo_bipado"
        verbose_name = "rolo bipado"
        verbose_name_plural = "rolos bipados"


class Painel(models.Model):
    nome = models.CharField(
        null=True, blank=True,
        max_length=64)
    layout = models.CharField(
        null=True, blank=True, max_length=4096,
        verbose_name='receita')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_ger_painel"
        verbose_name = "painel"


class PainelModulo(models.Model):
    nome = models.CharField(
        null=True, blank=True,
        max_length=64)
    TIPOS_DE_MODULOS = (('I', 'Informativo'),)
    tipo = models.CharField(
        max_length=1, choices=TIPOS_DE_MODULOS,
        default='I')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_ger_painel_modulo"
        verbose_name = "modulo de painel"
        verbose_name_plural = "modulos de painel"


class UsuarioPainelModulo(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    painel_modulo = models.ForeignKey(
        PainelModulo, on_delete=models.CASCADE,
        verbose_name='módulo de painel')

    class Meta:
        db_table = "fo2_ger_usr_pnl_modulo"
        verbose_name = "usuáio de modulo de painel"
        verbose_name_plural = "usuáios de modulos de painel"


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
    texto = models.CharField(
        null=True, blank=True, max_length=4096,
        verbose_name='receita')

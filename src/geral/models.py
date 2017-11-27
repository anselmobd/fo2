from django.db import models


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

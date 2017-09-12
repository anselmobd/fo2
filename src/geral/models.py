from django.db import models


class RecordTracking(models.Model):
    user = models.CharField(
        max_length=64, verbose_name='Usuário')
    time = models.DateTimeField(
        auto_now_add=False)
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
        verbose_name = "log de alteração de registro"
        verbose_name_plural = "logs de alterações de registros"

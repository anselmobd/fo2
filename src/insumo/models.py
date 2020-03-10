from django.utils import timezone
from django.db import models


class SugestaoCompra(models.Model):
    nivel = models.CharField(
        db_index=True, max_length=1,
        verbose_name='Nível')
    referencia = models.CharField(
        db_index=True, max_length=5,
        verbose_name='Referência')
    tamanho = models.CharField(
        db_index=True, max_length=3,
        verbose_name='Tamanho')
    ordem_tamanho = models.IntegerField(
        db_index=True, default=0,
        verbose_name='ordem tamanho')
    cor = models.CharField(
        db_index=True, max_length=6,
        verbose_name='Cor')
    data = models.DateTimeField(
        db_index=True,
        verbose_name='Data do calculo')
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Criada em')

    def save(self, *args, **kwargs):
        ''' On create, get timestamps '''
        # At create have no "id"
        if not self.id:
            self.create_at = timezone.now()
        super(SugestaoCompra, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_sugestao_compra"
        verbose_name = "Sugestão de compra"


class SugestaoCompraDatas(models.Model):
    sugestao = models.ForeignKey(
        SugestaoCompra, on_delete=models.CASCADE,
        db_index=True,
        verbose_name='Sugestão de compra')
    data_compra = models.DateField(
        db_index=True,
        verbose_name='Data de compra')
    data_recepcao = models.DateField(
        verbose_name='Data de recepção')
    qtd = models.DecimalField(
        max_digits=13, decimal_places=3,
        verbose_name='Quantidade')

    class Meta:
        db_table = "fo2_sugestao_compra_datas"
        verbose_name = "Datas da sugestão de compra"

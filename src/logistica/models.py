from django.db import models


class NotaFiscal(models.Model):
    # campos importados
    numero = models.IntegerField(
        db_index=True, unique=True, verbose_name='número')
    ativa = models.BooleanField(default=True)
    faturamento = models.DateTimeField(null=True, blank=True)
    cod_status = models.IntegerField(
        null=True, blank=True,
        verbose_name='status')
    msg_status = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='status (descr.)')
    dest_cnpj = models.CharField(
        max_length=20, null=True, blank=True,
        verbose_name='CNPJ')
    dest_nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Destinatário')
    natu_venda = models.BooleanField(default=False, verbose_name='venda')
    uf = models.CharField(
        max_length=2, null=True, blank=True,
        verbose_name='UF')
    natu_descr = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='natureza')
    transp_nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='transportadora')
    valor = models.DecimalField(
        decimal_places=2, max_digits=10,
        null=True, blank=True)
    volumes = models.IntegerField(
        null=True, blank=True)
    pedido = models.IntegerField(
        null=True, blank=True,
        verbose_name='pedido')
    ped_cliente = models.CharField(
        max_length=30, null=True, blank=True,
        verbose_name='pedido cliente')

    # campos editáveis
    saida = models.DateField(null=True, blank=True, verbose_name='saída')
    entrega = models.DateField(
        null=True, blank=True,
        verbose_name='agendamento')
    confirmada = models.BooleanField(
        default=False,
        verbose_name='entregue')
    observacao = models.TextField(
        null=True, blank=True,
        verbose_name='observação')

    class Meta:
        db_table = "fo2_fat_nf"
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"

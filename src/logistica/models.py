from django.db import models
from django.utils.text import slugify


class PosicaoCarga(models.Model):
    nome = models.CharField(
        max_length=20,
        db_index=True, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_pos_carga"
        verbose_name = "Posição de carga(NF)"
        verbose_name_plural = "Posições de carga(NF)"


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
    nf_devolucao = models.IntegerField(
        null=True, blank=True, verbose_name='Devolução')
    trail = models.CharField(
        db_index=True, max_length=32, null=True, blank=True, default='')
    posicao = models.ForeignKey(
        PosicaoCarga, default=1,
        verbose_name='Posição',
        on_delete=models.PROTECT)

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

    def save(self, *args, **kwargs):
        if self.id:
            if self.saida:
                if self.posicao.id != 3:
                    self.posicao = PosicaoCarga.objects.get(id=3)
            else:
                if self.posicao.id == 3:
                    self.posicao = PosicaoCarga.objects.get(id=1)
        if self.id:
            if self.confirmada:
                if self.posicao.id != 5:
                    self.posicao = PosicaoCarga.objects.get(id=5)
            else:
                if self.posicao.id == 5:
                    if self.saida:
                        self.posicao = PosicaoCarga.objects.get(id=3)
                    else:
                        self.posicao = PosicaoCarga.objects.get(id=1)
        super(NotaFiscal, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_fat_nf"
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"
        permissions = (("can_beep_shipment", "Can beep shipment"),
                       )


class RotinaLogistica(models.Model):
    nome = models.CharField(
        max_length=30,
        db_index=True, unique=True)
    slug = models.SlugField()

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_logist_rotina"
        verbose_name = "Rotina ligada à app Logistica"
        verbose_name_plural = "Rotinas ligadas à app Logistica"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nome)
        super(RotinaLogistica, self).save(*args, **kwargs)


class PosicaoCargaAlteracao(models.Model):
    inicial = models.ForeignKey(
        PosicaoCarga,
        verbose_name='Estado inicial',
        related_name='posicao_inicial_set',
        on_delete=models.PROTECT)
    ordem = models.IntegerField(default=0)
    descricao = models.CharField(
        'descrição', max_length=200)
    efeito = models.ForeignKey(
        RotinaLogistica, default=1,
        on_delete=models.PROTECT)
    final = models.ForeignKey(
        PosicaoCarga,
        verbose_name='Estado Final',
        related_name='posicao_final_set',
        on_delete=models.PROTECT)

    class Meta:
        db_table = "fo2_pos_carga_alt"
        verbose_name = "Alteração de posição de carga(NF)"
        verbose_name_plural = "Alterações de Posição de carga(NF)"


class PosicaoCargaAlteracaoLog(models.Model):
    numero = models.IntegerField(
        db_index=True, verbose_name='número')
    time = models.DateTimeField(
        db_index=True,
        auto_now_add=True, verbose_name='Hora')
    user = models.CharField(
        db_index=True,
        max_length=64, verbose_name='Usuário')
    inicial = models.ForeignKey(
        PosicaoCarga,
        verbose_name='Estado inicial',
        related_name='log_posicao_inicial_set',
        on_delete=models.PROTECT)
    final = models.ForeignKey(
        PosicaoCarga,
        verbose_name='Estado Final',
        related_name='log_posicao_final_set',
        on_delete=models.PROTECT)
    saida = models.DateField(null=True, blank=True, verbose_name='saída')

    class Meta:
        db_table = "fo2_pos_carga_alt_log"
        verbose_name = "Log de alteração de posição de carga(NF)"

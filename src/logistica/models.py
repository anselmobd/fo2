from pprint import pprint

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from utils.classes import LoggedInUser
from utils.functions.cadastro import CNPJ

from base.models import Empresa


class PosicaoCarga(models.Model):
    nome = models.CharField(max_length=20, db_index=True, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_pos_carga"
        verbose_name = "Posição de carga(NF)"
        verbose_name_plural = "Posições de carga(NF)"


class NotaFiscal(models.Model):
    # campos importados
    numero = models.IntegerField(db_index=True, unique=True, verbose_name="número")
    ativa = models.BooleanField(db_index=True, default=True)
    faturamento = models.DateTimeField(db_index=True, null=True, blank=True)
    cod_status = models.IntegerField(null=True, blank=True, verbose_name="status")
    msg_status = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="status (descr.)"
    )
    dest_cnpj = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="CNPJ"
    )
    dest_nome = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Destinatário"
    )
    natu_venda = models.BooleanField(db_index=True, default=False, verbose_name="venda")
    uf = models.CharField(max_length=2, null=True, blank=True, verbose_name="UF")
    natu_descr = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="natureza"
    )
    transp_nome = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="transportadora"
    )
    valor = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    volumes = models.IntegerField(null=True, blank=True)
    pedido = models.IntegerField(null=True, blank=True, verbose_name="pedido")
    ped_cliente = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="pedido cliente"
    )
    nf_devolucao = models.IntegerField(null=True, blank=True, verbose_name="Devolução")
    trail = models.CharField(
        db_index=True, max_length=32, null=True, blank=True, default=""
    )
    posicao = models.ForeignKey(
        PosicaoCarga, default=1, verbose_name="Posição", on_delete=models.PROTECT
    )

    # campos editáveis
    saida = models.DateField(null=True, blank=True, verbose_name="saída")
    entrega = models.DateField(null=True, blank=True, verbose_name="agendamento")
    confirmada = models.BooleanField(default=False, verbose_name="entregue")
    observacao = models.TextField(null=True, blank=True, verbose_name="observação")

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
        permissions = (("can_beep_shipment", "Can beep shipment"),)


class RotinaLogistica(models.Model):
    nome = models.CharField(max_length=30, db_index=True, unique=True)
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
        verbose_name="Estado inicial",
        related_name="posicao_inicial_set",
        on_delete=models.PROTECT,
    )
    ordem = models.IntegerField(default=0)
    descricao = models.CharField("descrição", max_length=200)
    efeito = models.ForeignKey(RotinaLogistica, default=1, on_delete=models.PROTECT)
    final = models.ForeignKey(
        PosicaoCarga,
        verbose_name="Estado Final",
        related_name="posicao_final_set",
        on_delete=models.PROTECT,
    )
    so_nfs_ativas = models.BooleanField(verbose_name="Só NFs ativas", default=True)

    class Meta:
        db_table = "fo2_pos_carga_alt"
        verbose_name = "Alteração de posição de carga(NF)"
        verbose_name_plural = "Alterações de Posição de carga(NF)"


class PosicaoCargaAlteracaoLog(models.Model):
    numero = models.IntegerField(db_index=True, verbose_name="número")
    time = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="Hora")
    user = models.CharField(db_index=True, max_length=64, verbose_name="Usuário")
    inicial = models.ForeignKey(
        PosicaoCarga,
        verbose_name="Estado inicial",
        related_name="log_posicao_inicial_set",
        on_delete=models.PROTECT,
    )
    final = models.ForeignKey(
        PosicaoCarga,
        verbose_name="Estado Final",
        related_name="log_posicao_final_set",
        on_delete=models.PROTECT,
    )
    saida = models.DateField(null=True, blank=True, verbose_name="saída")

    class Meta:
        db_table = "fo2_pos_carga_alt_log"
        verbose_name = "Log de alteração de posição de carga(NF)"


class NfEntrada(models.Model):

    # Obs.: Não consigo apagar pois está referenciado em uma migration
    def get_tussor():
        return None

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    cadastro = models.CharField("CNPJ", max_length=20, default="")
    emissor = models.CharField(max_length=200)
    numero = models.IntegerField("número")
    descricao = models.CharField("descrição", max_length=200)
    qtd = models.DecimalField("quantidade", max_digits=13, decimal_places=4)
    hora_entrada = models.TimeField("hora de entrada", default=timezone.now)
    transportadora = models.CharField(max_length=100)
    motorista = models.CharField(max_length=100)
    placa = models.CharField(max_length=10)
    responsavel = models.CharField("responsável", max_length=100)
    usuario = models.ForeignKey(User, models.PROTECT, verbose_name="usuário")
    quando = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        cnpj = CNPJ()
        cnpj.validate(self.cadastro)
        return f"{cnpj.mask(cnpj.cnpj)} NF {self.numero}"

    def clean_cadastro(self):
        val_cnpj = CNPJ()
        if val_cnpj.validate(self.cadastro):
            cadastro = val_cnpj.mask(val_cnpj.cnpj)
        else:
            raise ValidationError(f"Cadastro nacional inválido.")
        return cadastro

    def clean_usuario(self):
        logged_in = LoggedInUser()
        return logged_in.user

    def clean_quando(self):
        return timezone.now()

    def clean(self):
        self.cadastro = self.clean_cadastro()
        self.usuario = self.clean_usuario()
        self.quando = self.clean_quando()

    class Meta:
        db_table = "fo2_nf_entrada"
        verbose_name = "Nota fiscal de entrada"
        verbose_name_plural = "Notas fiscais de entrada"
        unique_together = [["cadastro", "numero"]]


class NfEntradaXManager(models.Manager):
    def __init__(self, nome):
        self.nome = nome
        super().__init__()

    def get_queryset(self):
        try:
            numero = Empresa.objects.get(nome=self.nome).numero
        except Exception:
            numero = 0
        return (
            super(NfEntradaXManager, self).get_queryset().filter(empresa__numero=numero)
        )


class NfEntradaAgator(NfEntrada):

    objects = NfEntradaXManager("AGATOR")

    def clean(self):
        try:
            self.empresa = Empresa.objects.get(nome="AGATOR")
        except Exception:
            raise ValidationError(f"Registro da Empresa 'AGATOR' não encontrado.")
        super(NfEntradaAgator, self).clean()

    class Meta:
        proxy = True
        verbose_name = "Nota fiscal de entrada Agator"
        verbose_name_plural = "Notas fiscais de entrada Agator"


class NfEntradaTussor(NfEntrada):

    objects = NfEntradaXManager("DUOMO")

    def clean(self):
        try:
            self.empresa = Empresa.objects.get(nome="DUOMO")
        except Exception:
            raise ValidationError(f"Registro da Empresa 'DUOMO' não encontrado.")
        super(NfEntradaTussor, self).clean()

    class Meta:
        proxy = True
        verbose_name = "Nota fiscal de entrada Tussor"
        verbose_name_plural = "Notas fiscais de entrada Tussor"

import pytz
from datetime import date, datetime, timedelta
from pprint import pprint

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from utils.classes import LoggedInUser
from utils.functions.cadastro import CNPJ, CPF

from base.models import Empresa


class PosicaoCarga(models.Model):
    nome = models.CharField(max_length=20, db_index=True, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_pos_carga"
        verbose_name = "Posição de carga(NF)"
        verbose_name_plural = "Posições de carga(NF)"


class NotaFiscalManager(models.Manager):

    def xfilter(
        self,
        data_de=None,
        data_ate=None,
        uf=None,
        nf=None,
        transportadora=None,
        cliente=None,
        pedido=None,
        ped_cliente=None,
        data_saida='N',
        entregue='T',
        ordem='A',
        listadas='T',
        posicao=None,
        tipo='-',
        **kwargs
    ):
        local = pytz.timezone("America/Sao_Paulo")

        filters = {}
        conditions = []
        order = None

        if data_de:
            datatime_de = datetime.combine(
                data_de, datetime.min.time())
            local_dt = local.localize(datatime_de, is_dst=None)
            dt_de = local_dt.astimezone(pytz.utc)
            filters['faturamento__gte'] = dt_de

        if data_ate:
            datatime_ate = datetime.combine(
                data_ate + timedelta(days=1), datetime.min.time())
            local_ate_dt = local.localize(datatime_ate, is_dst=None)
            dt_ate = local_ate_dt.astimezone(pytz.utc)
            filters['faturamento__lte'] = dt_ate

        if uf:
            filters['uf'] = uf

        if nf:
            filters['numero'] = nf

        if transportadora:
            filters['transp_nome__icontains'] = transportadora

        if cliente:
            conditions.append(
                models.Q(dest_nome__icontains=cliente) | \
                models.Q(dest_cnpj__contains=cliente)
            )

        if pedido:
            filters['pedido'] = pedido

        if ped_cliente:
            filters['ped_cliente'] = ped_cliente

        if data_saida != 'N':
            filters['saida__isnull'] = data_saida == 'S'

        if entregue != 'T':
            filters['confirmada'] = entregue == 'S'

        if ordem == 'N':
            order = '-numero'
        elif ordem == 'P':
            order = 'pedido'

        if listadas.upper() == 'V':
            filters.update({
                'natu_venda' : True,
                'ativa': True,
            })

        if posicao:
            filters['posicao_id'] = posicao.id

        if tipo != '-':
            filters['tipo'] = tipo

        select = super(NotaFiscalManager, self).get_queryset()

        if filters:
            select = select.filter(**filters)

        if conditions:
            for condition in conditions:
                select = select.filter(condition)

        if order:
            select = select.order_by(order)

        return select


class NotaFiscal(models.Model):
    # campos importados
    EMPRESA = (
        (1, 'Tussor'),
        (2, 'Agator'),
        (3, 'Corte'),
        (4, 'Gavi'),
    )
    empresa = models.SmallIntegerField(
        db_index=True,
        choices=EMPRESA,
        default=1,
    )
    numero = models.IntegerField(db_index=True, verbose_name="número")
    ativa = models.BooleanField(db_index=True, default=True)
    data_base = models.DateField(
        db_index=True, default=date(2001, 1, 2), verbose_name="Data base")
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
    quantidade = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    pedido = models.IntegerField(null=True, blank=True, verbose_name="pedido")
    ped_cliente = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="pedido cliente"
    )
    nf_devolucao = models.IntegerField(null=True, blank=True, verbose_name="Devolução")
    trail = models.CharField(
        db_index=True, max_length=33, null=True, blank=True, default=""
    )
    posicao = models.ForeignKey(
        PosicaoCarga, default=1, verbose_name="Posição", on_delete=models.PROTECT
    )

    ATACADO = 'a'
    VAREJO = 'v'
    OUTROS = 'o'
    TIPO_NOTA = (
        (ATACADO, "Atacado"),
        (VAREJO, "Varejo"),
        (OUTROS, "")
    )
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_NOTA,
        default=OUTROS,
    )

    # campos editáveis
    saida = models.DateField(null=True, blank=True, verbose_name="saída")
    entrega = models.DateField(null=True, blank=True, verbose_name="agendamento")
    confirmada = models.BooleanField(default=False, verbose_name="entregue")
    observacao = models.TextField(null=True, blank=True, verbose_name="observação")
    comprovante = models.BooleanField(default=False, verbose_name="Com comprovante")

    objects = NotaFiscalManager()

    def __str__(self, *args, **kwargs):
        return f"NF ({dict(self.EMPRESA)[self.empresa]}) {self.numero}"

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
        unique_together = (("empresa", "numero"),)


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

    SERVICO = 's'
    VENDA = "v"
    INDEFINIDO = "_"
    TIPO_NOTA = (
        (SERVICO, "Serviço"),
        (VENDA, "Venda"),
        (INDEFINIDO, "")
    )

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    cadastro = models.CharField("CNPJ/CPF", max_length=20, default="")
    emissor = models.CharField(max_length=200)
    numero = models.IntegerField("número")
    tipo = models.CharField(
        max_length=1,
        choices=TIPO_NOTA,
        default=VENDA,
    )
    descricao = models.CharField("descrição", max_length=200)
    volumes = models.IntegerField()
    chegada = models.DateTimeField("chegada", default=timezone.now)
    transportadora = models.CharField(max_length=100)
    motorista = models.CharField(max_length=100)
    placa = models.CharField(max_length=10)
    responsavel = models.CharField("responsável", max_length=100)
    usuario = models.ForeignKey(User, models.PROTECT, verbose_name="usuário")
    quando = models.DateTimeField(null=True, editable=False)

    def __str__(self):
        val_cnpj = CNPJ()
        if val_cnpj.validate(self.cadastro):
            cadastro = val_cnpj.mask(val_cnpj.cnpj)
        else:
            val_cpf = CPF()
            if val_cpf.validate(self.cadastro):
                cadastro = val_cpf.mask(val_cpf.cpf)
            else:
                cadastro = self.cadastro
        return f"{cadastro} NF{self.tipo} {self.numero}"

    def clean_cadastro(self):
        val_cnpj = CNPJ()
        if val_cnpj.validate(self.cadastro):
            cadastro = val_cnpj.mask(val_cnpj.cnpj)
        else:
            val_cpf = CPF()
            if val_cpf.validate(self.cadastro):
                cadastro = val_cpf.mask(val_cpf.cpf)
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
        unique_together = [["cadastro", "numero", "tipo"]]


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

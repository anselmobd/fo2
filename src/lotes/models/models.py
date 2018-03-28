from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Impresso(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impresso"
        verbose_name = "Impresso"


class ModeloTermica(models.Model):
    codigo = models.CharField(
        unique=True, max_length=20, null=True, blank=True,
        verbose_name='código')
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='nome')

    # Tive problemas com esse campo pois ficou com tamanho 2048, sem forma
    # de definir novo tamanho. Tive que passar para CharField
    # modelo = models.TextField(
    #     null=True, blank=True,
    #     verbose_name='modelo')

    # Tive problemas novamente. Mensagem reclamendo de 2048. Não entendi.
    # Só criando outro campo consegui voltar ao trabalho.
    # receita = models.CharField(
    #     null=True, blank=True, max_length=8192,
    #     verbose_name='receita')

    gabarito = models.CharField(
        null=True, blank=True, max_length=8192,
        verbose_name='gabarito')
    campos = models.TextField(
        null=True, blank=True,
        verbose_name='campos')

    def __str__(self):
        return self.codigo

    class Meta:
        db_table = "fo2_lot_modelo_termica"
        verbose_name = "modelo de etiqueta térmica"
        verbose_name_plural = "modelos de etiqueta térmica"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo and self.codigo.upper()
        super(ModeloTermica, self).save(*args, **kwargs)


class ImpressoraTermica(models.Model):
    nome = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name='Nome')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "fo2_lot_impr_termica"
        verbose_name = "impressora térmica"
        verbose_name_plural = "impressoras térmicas"


class UsuarioImpresso(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='usuário')
    impresso = models.ForeignKey(
        Impresso, on_delete=models.CASCADE,
        verbose_name='impresso')
    impressora_termica = models.ForeignKey(
        ImpressoraTermica, on_delete=models.CASCADE,
        verbose_name='impressora térmica')
    modelo = models.ForeignKey(
        ModeloTermica, on_delete=models.CASCADE,
        verbose_name='modelo padrão')

    class Meta:
        db_table = "fo2_lot_usuario_impresso"
        verbose_name = "Impressos de usuário"
        verbose_name_plural = "Impressos de usuários"
        unique_together = ("usuario", "impresso")


class Lote(models.Model):
    lote = models.CharField(
        max_length=20, verbose_name='lote')
    op = models.IntegerField(
        null=True, blank=True,
        verbose_name='OP')
    referencia = models.CharField(
        max_length=5, verbose_name='Referência')
    tamanho = models.CharField(
        max_length=3, verbose_name='Tamanho')
    cor = models.CharField(
        max_length=6, verbose_name='Cor')
    qtd_produzir = models.IntegerField(
        verbose_name='quantidade')
    create_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='criado em')
    update_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='alterado em')

    def save(self, *args, **kwargs):
        ''' On create and update, get timestamps '''
        if self.id:
            self.update_at = timezone.now()
        else:  # At create have no "id"
            self.create_at = timezone.now()
        return super(Lote, self).save(*args, **kwargs)

    class Meta:
        db_table = "fo2_cd_lote"
        verbose_name = "lote"

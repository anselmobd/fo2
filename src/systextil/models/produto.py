from django.db import models


class Colecao(models.Model):
    colecao = models.IntegerField(primary_key=True)
    descr_colecao = models.CharField(
        max_length=100,
        verbose_name='Descrição')

    def __str__(self):
        return f"{self.colecao}-{self.descr_colecao}"

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_140"
        verbose_name = "Coleção"


class Familia(models.Model):
    divisao_producao = models.IntegerField(primary_key=True)
    descricao = models.CharField(
        max_length=20,
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}'.format(self.divisao_producao, self.descricao)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_180"
        verbose_name = "Família"


class LinhaNivel1Manager(models.Manager):
    def get_queryset(self):
        return super(LinhaNivel1Manager, self).get_queryset().exclude(
            linha_produto=0,
        ).filter(
            nivel_estrutura=1,
        )


class LinhaNivel1(models.Model):
    linha_produto = models.IntegerField(
        primary_key=True,
        verbose_name='Linha',
    )
    nivel_estrutura = models.IntegerField(
        verbose_name='Nível',
    )
    descricao_linha = models.CharField(
        max_length=20,
        verbose_name='Descrição',
    )

    objects = LinhaNivel1Manager()

    def __str__(self):
        return '{}-{}'.format(self.linha_produto, self.descricao_linha)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_120"
        verbose_name = "Linha de Produto Nível 1"


class Produto(models.Model):
    nivel_estrutura = models.CharField(
        max_length=1,
        verbose_name='Nível')
    referencia = models.CharField(
        max_length=5,
        verbose_name='Referência')

    def __str__(self):
        return '{}.{}'.format(self.nivel_estrutura, self.referencia)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_030"
        verbose_name = "Produto (Systêxtil)"


class Tamanho(models.Model):
    tamanho_ref = models.CharField(
        primary_key=True,
        max_length=3,
        verbose_name='Código')
    descr_tamanho = models.CharField(
        max_length=10,
        verbose_name='Descrição')
    ordem_tamanho = models.IntegerField(
        verbose_name='Ordem do tamanho')

    def __str__(self):
        return self.descr_tamanho

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_220"
        verbose_name = "Tamanho (Systêxtil)"

from django.db import models


class Servidor(models.Model):
    descricao = models.CharField(
        unique=True, max_length=200, verbose_name='descrição')
    hostname = models.CharField(unique=True, max_length=50)
    ip4 = models.CharField(unique=True, max_length=15)
    port = models.IntegerField(default=22, verbose_name='porta ssh')
    user = models.CharField(
        max_length=50, default=None, verbose_name='usuário')
    key_file = models.FileField(
        null=True, blank=True,
        upload_to="upload/remote_files/servidor",
        verbose_name='Chave pública')

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = 'fo2_rfile_servidor'
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'


class Diretorio(models.Model):
    servidor = models.ForeignKey(Servidor, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=200, verbose_name='descrição')
    caminho = models.CharField(max_length=300)
    file_perm = models.IntegerField(verbose_name='permissões (octal)')
    file_user = models.CharField(max_length=50, verbose_name='usuário')
    file_group = models.CharField(max_length=50, verbose_name='grupo')

    def __str__(self):
        return f'{self.servidor.descricao} / {self.descricao}'

    class Meta:
        db_table = 'fo2_rfile_folder'
        verbose_name = 'Diretório'

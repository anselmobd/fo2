import os
import subprocess
from pprint import pprint

from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View

import email_signature.models as models
from email_signature.views.views import get_template_file


class GerarAssinaturas(View):

    def __init__(self):
        self.template_name = 'email_signature/gerar_assinaturas.html'
        self.context = {'titulo': 'Gerar assinaturas'}
        self.temp_file = '_temp_assinatura_file_.html'
        self.transf = {}

    def gerar_assinatura_local(self, conta):
        context = {
            'nome': conta.nome,
            'setor': '' if conta.setor is None else conta.setor,
            'email': conta.email,
            'ddd_1': conta.ddd_1,
            'num_1': conta.num_1,
            'ddd_2': conta.ddd_2,
            'num_2': conta.num_2,
        }
        try:
            assinatura = render_to_string(self.template_file, context)
            arquivo = os.path.join('.', self.temp_file)
            with open(arquivo, 'w') as index:
                index.write(assinatura)
        except Exception:
            return 'Erro'

    def apagar_assinatura_local(self):
        arquivo = os.path.join('.', self.temp_file)
        try:
            os.remove(arquivo)
        except FileNotFoundError:
            pass

    def decode_rstrip(self, lines):
        output = []
        for line in lines:
            output.append(line.decode().rstrip())
        return output

    def executa_comando(self, comando):
        ssh = subprocess.Popen(comando, shell=False, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = self.decode_rstrip(ssh.stdout.readlines())
        error = self.decode_rstrip(ssh.stderr.readlines())
        streamdata = ssh.communicate()[0]
        returncode = ssh.returncode
        return returncode, result, error

    def executa_comando_ssh(self, comando):
        if self.transf['key_file']:
            ssh_call = [
                "ssh", "-p", self.transf['port'],
                "-i", self.transf['key_file'],
                self.transf['user@server']]
        else:
            ssh_call = [
                "ssh", "-p", self.transf['port'],
                self.transf['user@server']]
        return self.executa_comando(ssh_call + comando)

    def executa_comando_scp(self, comando):
        if self.transf['key_file']:
            ssh_call = ["scp", "-P", self.transf['port'],
                        "-i", self.transf['key_file']]
        else:
            ssh_call = ["scp", "-P", self.transf['port']]
        return self.executa_comando(ssh_call + comando)

    def scape_dirname(self, dirname):
        result = []
        for caractere in dirname:
            is_alfanum = caractere.isalnum()
            is_simbolo = caractere in '/._-'
            is_valido = is_alfanum or is_simbolo
            if not is_valido:
                caractere = f'\{caractere}'
            result.append(caractere)
        return ''.join(result)

    def mount_transfer_parameters(self, conta):
        diretorio = conta.diretorio
        servidor = diretorio.servidor

        self.transf['hostname'] = servidor.hostname
        self.transf['port'] = str(servidor.port)
        self.transf['user@server'] = f"{servidor.user}@{servidor.ip4}"
        self.transf['key_file'] = servidor.key_file.path

        caminho = diretorio.caminho.strip('/')
        subdiretorio = conta.subdiretorio.strip('/')
        caminho_completo = os.path.join('/', caminho, subdiretorio)
        dir_servidor = os.path.normpath(caminho_completo)
        self.transf['dir_servidor'] = self.scape_dirname(dir_servidor)

        usuario = self.scape_dirname(conta.email.split('@')[0])
        arquivo = f'assinatura_{usuario}.html'
        self.transf['arquivo_path'] = os.path.join(dir_servidor, arquivo)

        self.transf['file_perm'] = diretorio.file_perm
        self.transf['file_user'] = diretorio.file_user
        self.transf['file_group'] = diretorio.file_group

    def enviar_assinatura(self, conta):
        self.mount_transfer_parameters(conta)

        exitcode, result, error = self.executa_comando_ssh(["hostname"])
        if exitcode != 0:
            return 'Sem acesso ao servidor'
        if result[0] != self.transf['hostname']:
            return 'Configuração de servidor errada'

        exitcode, result, error = self.executa_comando_ssh(
            [f"stat -c '%A %U %G' '{self.transf['dir_servidor']}/'"])
        if exitcode != 0:
            return 'Erro acessando diretório'
        # if result[0] != 'drwxrwxrwx nobody nogroup':
        #     return 'Diretório com direitos não esperados'

        exitcode, result, error = self.executa_comando_scp(
            [self.temp_file,
             f"{self.transf['user@server']}:{self.transf['arquivo_path']}"])
        if exitcode != 0:
            return 'Erro copiando arquivo'

        stat_index = os.stat(self.temp_file)

        exitcode, result, error = self.executa_comando_ssh(
            [f"stat -c '%s' '{self.transf['arquivo_path']}'"])
        if exitcode != 0:
            return 'Erro verificando o arquivo'
        if result[0] != str(stat_index.st_size):
            return 'Arquivo com tamanho errado'

        exitcode, result, error = self.executa_comando_ssh(
            [f"chmod {self.transf['file_perm']} "
             f"'{self.transf['arquivo_path']}'"])
        if exitcode != 0:
            return 'Erro acertando permissões'

        exitcode, result, error = self.executa_comando_ssh(
            [f"chown {self.transf['file_user']}:{self.transf['file_group']} "
             f"'{self.transf['arquivo_path']}'"])
        if exitcode != 0:
            return 'Erro acertando dono e grupo'

    def mount_context(self, **kwargs):
        self.template_file = get_template_file()

        self.id = None
        if 'id' in kwargs:
            self.id = kwargs['id']

        if self.id is None:
            contas = models.Account.objects.all()
        else:
            contas = models.Account.objects.filter(id=self.id)
        self.context['lista'] = []

        for conta in contas:

            erro = self.gerar_assinatura_local(conta)
            if erro is None:
                erro = self.enviar_assinatura(conta)
            self.apagar_assinatura_local()

            self.context['lista'].append(dict(
                conta=conta.email,
                erro=erro,
            ))

    def get(self, request, *args, **kwargs):
        self.mount_context(**kwargs)
        return render(request, self.template_name, self.context)

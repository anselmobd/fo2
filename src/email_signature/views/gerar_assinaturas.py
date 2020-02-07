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

    def gerar_assinatura_local(self, conta):
        context = {
            'nome': conta.nome,
            'setor': conta.setor,
            'email': conta.email,
            'num_1': conta.num_1,
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
        os.remove(arquivo)

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
        if settings.SSH_IDENTITY_FILE:
            ssh_call = ["ssh", "-p", "922",
                        "-i", settings.SSH_IDENTITY_FILE,
                        "root@192.168.1.100"]
        else:
            ssh_call = ["ssh", "-p", "922", "root@192.168.1.100"]
        return self.executa_comando(ssh_call + comando)

    def executa_comando_scp(self, comando):
        if settings.SSH_IDENTITY_FILE:
            ssh_call = ["scp", "-P", "922",
                        "-i", settings.SSH_IDENTITY_FILE]
        else:
            ssh_call = ["scp", "-P", "922"]
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

    def enviar_assinatura(self, conta):
        exitcode, result, error = self.executa_comando_ssh(["hostname"])
        if exitcode != 0:
            return 'Sem acesso ao servidor'
        if result[0] != 'servidor':
            return 'Configuração de servidor errada'

        dir_servidor = self.scape_dirname(conta.dir_servidor)

        exitcode, result, error = self.executa_comando_ssh(
            [f"stat -c '%A %U %G' '{dir_servidor}/'"])
        if exitcode != 0:
            return 'Erro acessando diretório'
        if result[0] != 'drwxrwxrwx nobody nogroup':
            return 'Diretório com direitos não esperados'

        arquivo = self.scape_dirname(conta.arquivo)

        exitcode, result, error = self.executa_comando_scp(
            [self.temp_file,
             f"root@192.168.1.100:{dir_servidor}/{arquivo}"])
        if exitcode != 0:
            return 'Erro copiando arquivo'

        stat_index = os.stat(self.temp_file)

        exitcode, result, error = self.executa_comando_ssh(
            [f"stat -c '%s' '{dir_servidor}/{arquivo}'"])
        if exitcode != 0:
            return 'Erro verificando o arquivo'
        if result[0] != str(stat_index.st_size):
            return 'Arquivo com tamanho errado'

        exitcode, result, error = self.executa_comando_ssh(
            [f"chmod 777 '{dir_servidor}/{arquivo}'"])
        if exitcode != 0:
            return 'Erro acertando permissões'

        exitcode, result, error = self.executa_comando_ssh(
            [f"chown nobody:nogroup '{dir_servidor}/{arquivo}'"])
        if exitcode != 0:
            return 'Erro acertando dono e grupo'

    def mount_context(self):
        self.template_file = get_template_file()

        contas = models.Account.objects.all()
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
        self.mount_context()
        return render(request, self.template_name, self.context)

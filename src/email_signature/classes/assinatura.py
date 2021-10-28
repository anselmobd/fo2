import os
import subprocess
import tempfile
from pprint import pprint

from django.template.loader import render_to_string

import email_signature.functions as functions


class GeraAssinatura():

    def __init__(self, conta):
        self.conta = conta
        tf = tempfile.NamedTemporaryFile(prefix=f"_{conta.id}_temp_assinatura_file_", suffix=".html")
        self.temp_file = tf.name
        self.nome_de_arquivo = os.path.join('.', self.temp_file)
        self.transf = {}

    def apagar_assinatura_local(self):
        try:
            os.remove(self.nome_de_arquivo)
        except FileNotFoundError:
            pass

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
        except Exception:
            return 'Erro', 'Renderizando template'
        try:
            with open(self.nome_de_arquivo, 'w') as arquivo:
                arquivo.write(assinatura)
        except Exception:
            return 'Erro', 'Escrevendo arquivo'
        return None, None

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
            return 'Sem acesso ao servidor', error
        if result[0] != self.transf['hostname']:
            return 'Configuração de servidor errada', error

        exitcode, result, error = self.executa_comando_ssh(
            [f"stat -c '%A %U %G' '{self.transf['dir_servidor']}/'"])
        if exitcode != 0:
            return 'Erro acessando diretório', error
        # if result[0] != 'drwxrwxrwx nobody nogroup':
        #     return 'Diretório com direitos não esperados'

        exitcode, result, error = self.executa_comando_scp(
            [self.temp_file,
             f"{self.transf['user@server']}:{self.transf['arquivo_path']}"])
        if exitcode != 0:
            return 'Erro copiando arquivo', error

        stat_index = os.stat(self.temp_file)

        exitcode, result, error = self.executa_comando_ssh(
            [f"stat -c '%s' '{self.transf['arquivo_path']}'"])
        if exitcode != 0:
            return 'Erro verificando o arquivo', error
        if result[0] != str(stat_index.st_size):
            return 'Arquivo com tamanho errado', error

        exitcode, result, error = self.executa_comando_ssh(
            [f"chmod {self.transf['file_perm']} "
             f"'{self.transf['arquivo_path']}'"])
        if exitcode != 0:
            return 'Erro acertando permissões', error

        exitcode, result, error = self.executa_comando_ssh(
            [f"chown {self.transf['file_user']}:{self.transf['file_group']} "
             f"'{self.transf['arquivo_path']}'"])
        if exitcode != 0:
            return 'Erro acertando dono e grupo', error

        return None, None

    def exec(self):
        self.template_file = functions.gets.get_template_file(self.conta.tipo)

        self.apagar_assinatura_local()
        erro, msg = self.gerar_assinatura_local(self.conta)
        if erro is None:
            erro, msg = self.enviar_assinatura(self.conta)
            self.conta.state = "N"
            self.conta.save()
        self.apagar_assinatura_local()
        
        return erro, msg

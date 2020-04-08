import subprocess
from pprint import pprint

from django.conf import settings


def decode_rstrip(lines):
    output = []
    for line in lines:
        output.append(line.decode().rstrip())
    return output


def executa_comando(comando):
    ssh = subprocess.Popen(
        comando, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = decode_rstrip(ssh.stdout.readlines())
    error = decode_rstrip(ssh.stderr.readlines())
    streamdata = ssh.communicate()[0]
    returncode = ssh.returncode
    return returncode, result, error


def executa_comando_ssh(user, server, port, key_file, comando):
    ssh_call = [
        "ssh", "-p", str(port),
        "-i", key_file,
        f'{user}@{server}',
        comando
        ]
    return executa_comando(ssh_call)


def router_add_ip_to_list(ip_list, ip):
    return executa_comando_ssh(
        settings.MIKROTIK['user'],
        '192.168.1.99',
        '22',
        settings.MIKROTIK['key_file'],
        f"/ip firewall address-list add list={ip_list} "
        f"address={ip}/32 timeout=00:00:11"
    )


def router_add_ip_to_apoio_auth():
    returncode, result, error = router_add_ip_to_list('apoio_auth', '8.7.6.5')
    pprint([returncode, result, error])

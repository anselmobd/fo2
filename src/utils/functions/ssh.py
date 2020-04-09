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


def executa_comando_ssh_exec(exec):
    return executa_comando_ssh(
        settings.MIKROTIK['user'],
        '192.168.1.99',
        '22',
        settings.MIKROTIK['key_file'],
        exec,
    )


def base_router_add_ip_to_list(ip_list, ip):
    return executa_comando_ssh_exec(
        f"/ip firewall address-list add list={ip_list} "
        f"address={ip}/32 timeout=00:01:00"
    )


def base_router_list_ips():
    return executa_comando_ssh_exec(
        "/ip firewall address-list print")


def router_list_ips():
    returncode, result, error = base_router_list_ips()

    data = {
        'returncode': returncode,
        'result': result,
        'error': error,
    }

    return data


def router_add_ip_to_list(ip_list, ip):
    returncode, result, error = base_router_add_ip_to_list(
        ip_list, ip)

    data = {
        'returncode': returncode,
        'result': result,
        'error': error,
    }

    data.update({
        'access': 'OK' if returncode == 0 else 'ERROR',
    })
    if returncode == 0:

        data.update({
            'command': 'OK' if len(error) == 0 else 'ERROR',
        })
        if len(error) == 0:

            action_error = False
            if len(result) != 0:
                action_error = (
                    result[0].startswith('failure') or
                    result[0].startswith('bad command')
                )

            data.update({
                'action': (
                    'ERROR' if action_error else 'OK'),
            })

    return data


def executa_comando_nivel_ok(data):
    result = 0
    if data['access'] == 'OK':
        result += 1
        if data['command'] == 'OK':
            result += 1
            if data['action'] == 'OK':
                result += 1
    return result


def router_add_ip_apoio_auth(ip):

    data = router_add_ip_to_list('apoio_auth', ip)
    if executa_comando_nivel_ok(data) != 3:
        data = router_list_ips()
        # data = router_add_ip_to_list('apoio_auth_redun', ip)

    return data

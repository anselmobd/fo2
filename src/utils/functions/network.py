import subprocess


def ping(ip_name, count=3):
    erros = []
    for _ in range(count):
        output = subprocess.run(["ping", "-c1", "-w1", ip_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode:
            erros.append(output)
        else:
            break
    return len(erros) != count, erros

import subprocess
from pprint import pprint


def fo2_ping(ip_name, count=3):
    erros = []
    for _ in range(count):
        output = subprocess.run(["ping", "-c1", "-w1", ip_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode:
            erros.append(output)
        else:
            break
    return len(erros) != count, erros


ip_addr = '10.0.0.4'  # input('Enter ip or url: ')
ip_addr = 'oc.tussor.com.br'  # input('Enter ip or url: ')

pprint(fo2_ping(ip_addr))

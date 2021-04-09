import csv
import re
from pprint import pprint

mail_set=set()
with open('../clientes.csv', newline='') as csvfile:
    clientes = csv.reader(csvfile, delimiter=';', quotechar='"')
    for cliente in clientes:
        # pprint(cliente)
        nome = cliente[0].title().strip()
        if nome == 'Nome_cliente':
            continue

        mail_com = cliente[1].lower()
        mail_com_list = re.findall(r"[\+0-9a-z.@_-]+", mail_com)
        for mail_item in mail_com_list:
            if mail_item.find("@cuecasduomo.com") == -1:
                mail_set.add((nome, mail_item))

        mail_nf = cliente[2].lower()
        mail_nf_list = re.findall(r"[\+0-9a-z.@_-]+", mail_nf)
        for mail_item in mail_nf_list:
            if mail_item.find("@cuecasduomo.com") == -1:
                mail_set.add((nome, mail_item))

# pprint(mail_set)
with open('../mails.csv', 'w', newline='') as csvfile:
    mails = csv.writer(
        csvfile, delimiter=';',
        quotechar='"'
    )
    for mail in list(mail_set):
        mails.writerow(mail)

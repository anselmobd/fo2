import datetime
import operator
import os
import tempfile
from dbfread import DBF
from smb.SMBConnection import SMBConnection
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from systextil.queries.op.referencia import referencias_com_op
from systextil.queries.faturamento.referencia import referencias_vendidas

from utils.functions.strings import only_digits


class ListaReferencias(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'comercial/lista_referencias.html'
        self.context = {'titulo': 'Lista referências'}

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        dt_old = datetime.date(2000, 1, 1)

        # There will be some mechanism to capture userID, password,
        # client_machine_name, server_name and server_ip
        # client_machine_name can be an arbitary ASCII string
        # server_name should match the remote machine name, or else
        # the connection will be rejected
        conn = SMBConnection('', '', 'localhost', 'arquivos.t', use_ntlm_v2 = True)
        assert conn.connect('arquivos.t', 139)

        file_obj = tempfile.NamedTemporaryFile(delete=False)  # 'wb', delete=False)
        file_attributes, filesize = conn.retrieveFile('teg', '/Tussor/bd/DIS_BAR.DBF', file_obj)
        # Retrieved file contents are inside file_obj
        # Do what you need with the file_obj and then close it
        # Note that the file obj is positioned at the end-of-file,
        # so you might need to perform a file_obj.seek() if you need
        # to read from the beginning

        file_obj.close()

        refs_old = set()
        with DBF(file_obj.name) as bars:
            for bar in bars:
                if bar['B_DESLIG'] is None:
                    refs_old.add(bar['B_PROD'])

        os.unlink(file_obj.name)

        modelos_op = {}
        refs_op = referencias_com_op(cursor)
        for row in refs_op:
            digits = only_digits(row['ref'])
            if digits:
                digits = int(digits)
                if digits in modelos_op:
                    modelos_op[digits] = max(
                        modelos_op[digits],
                        row['dt_digitacao'],
                    )
                else:
                    modelos_op[digits] = row['dt_digitacao']

        modelos_vendidos = {}
        refs_vendidos = referencias_vendidas(cursor)
        for row in refs_vendidos:
            digits = only_digits(row['ref'])
            if digits:
                digits = int(digits)
                if digits in modelos_vendidos:
                    modelos_vendidos[digits] = max(
                        modelos_vendidos[digits],
                        row['data_emissao'],
                    )
                else:
                    modelos_vendidos[digits] = row['data_emissao']

        modelos = {}
        for ref in refs_old:
            modelo = int(only_digits(ref))
            if modelo in modelos:
                modelos[modelo].append(ref)
            else:
                modelos[modelo] = [ref]

        dados_op = []
        for modelo in modelos:
            dados_op.append({
                'modelo': f"{modelo}",
                'ref': ", ".join(sorted(modelos[modelo])),
                'op': modelos_op[modelo].date() if modelo in modelos_op else dt_old,
                'nf': modelos_vendidos[modelo].date() if modelo in modelos_vendidos else 'Sem NF',
            })
        
        dados_op.sort(key=operator.itemgetter('op'))

        for row in dados_op:
            if row['op'] == dt_old:
                row['op'] = 'Sem OP'
        
        dados = dados_op.copy()
        dados.sort(key=operator.itemgetter('modelo'))


        self.context.update({
            'headers': [
                'Referências no sistema antigo',
                'Modelo',
                'Data da última OP do modelo',
                'Data da última venda do modelo',
            ],
            'fields': ['ref', 'modelo', 'op', 'nf'],
            'style': {2: 'text-align: right;'},
            'data': dados,
            'data_op': dados_op,
        })

    def get(self, request, *args, **kwargs):
        self.request = request
        self.mount_context()
        return render(request, self.template_name, self.context)

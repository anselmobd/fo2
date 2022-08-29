import operator
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

        # There will be some mechanism to capture userID, password, client_machine_name, server_name and server_ip
        # client_machine_name can be an arbitary ASCII string
        # server_name should match the remote machine name, or else the connection will be rejected
        conn = SMBConnection('', '', 'localhost', 'arquivos.t', use_ntlm_v2 = True)
        assert conn.connect('arquivos.t', 139)

        file_obj = tempfile.NamedTemporaryFile()  # 'wb', delete=False)
        file_attributes, filesize = conn.retrieveFile('teg', '/Tussor/bd/DIS_BAR.DBF', file_obj)
        # Retrieved file contents are inside file_obj
        # Do what you need with the file_obj and then close it
        # Note that the file obj is positioned at the end-of-file,
        # so you might need to perform a file_obj.seek() if you need
        # to read from the beginning

        refs_old = set()
        with DBF(file_obj.name) as bars:
            print('DBF')
            for bar in bars:
                if bar['B_DESLIG'] is None:
                    refs_old.add(bar['B_PROD'])

        file_obj.close()

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

        modelos_vendidos = set()
        refs_vendidos = referencias_vendidas(cursor)
        for row in refs_vendidos:
            digits = only_digits(row['ref'])
            if digits:
                modelos_vendidos.add(int(digits))

        dados = []
        for ref in refs_old:
            modelo = int(only_digits(ref))
            dados.append({
                'modelo': modelo,
                'ref': ref,
                'op': modelos_op[modelo].date() if modelo in modelos_op else 'Sem OP',
                'nf': 'S' if modelo in modelos_vendidos else 'N',
            })
        
        dados.sort(key=operator.itemgetter('modelo', 'ref'))

        self.context.update({
            'headers': [
                'Referência sistema antigo',
                'Modelo',
                'Data da última OP do modelo',
                'Modelo vendido',
            ],
            'fields': ['ref', 'modelo', 'op', 'nf'],
            'data': dados,
        })

    def get(self, request, *args, **kwargs):
        self.request = request
        self.mount_context()
        return render(request, self.template_name, self.context)

import operator
import tempfile
from dbfread import DBF
from smb.SMBConnection import SMBConnection
from pprint import pprint

from django.shortcuts import render
from django.views import View

from utils.functions.strings import only_digits


class ListaReferencias(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'comercial/lista_referencias.html'
        self.context = {'titulo': 'Lista referências'}

    def mount_context(self):

        # There will be some mechanism to capture userID, password, client_machine_name, server_name and server_ip
        # client_machine_name can be an arbitary ASCII string
        # server_name should match the remote machine name, or else the connection will be rejected
        conn = SMBConnection('', '', 'localhost', 'arquivos.t', use_ntlm_v2 = True)
        assert conn.connect('arquivos.t', 139)

        file_obj = tempfile.NamedTemporaryFile('wb', delete=False)
        file_attributes, filesize = conn.retrieveFile('teg', '/Tussor/bd/DIS_BAR.DBF', file_obj)
        # Retrieved file contents are inside file_obj
        # Do what you need with the file_obj and then close it
        # Note that the file obj is positioned at the end-of-file,
        # so you might need to perform a file_obj.seek() if you need
        # to read from the beginning
        file_obj.close()

        refs = set()
        with DBF(file_obj.name) as bars:
            print('DBF')
            for bar in bars:
                if bar['B_DESLIG'] is None:
                    refs.add(bar['B_PROD'])

        dados = []
        for ref in refs:
            dados.append({
                'modelo': int(only_digits(ref)),
                'ref': ref,
            })
        
        dados.sort(key=operator.itemgetter('modelo', 'ref'))

        self.context.update({
            'headers': ['Modelo', 'Referência sistema antigo'],
            'fields': ['modelo', 'ref'],
            'data': dados,
        })

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)

import datetime
import operator
import os
import tempfile
from collections import defaultdict
from dbfread import DBF
from smb.SMBConnection import SMBConnection
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from systextil.queries.op.referencia import referencias_com_op
from systextil.queries.faturamento.referencia import referencias_vendidas

from utils.functions.strings import only_digits
from utils.classes.classes import Max

from lotes.functions.varias import modelo_de_ref


class ListaReferencias(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'comercial/lista_referencias.html'
        self.context = {'titulo': 'Lista referências de modelo'}

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

        modelo_refs = defaultdict(list)
        for ref in refs_old:
            modelo_refs[modelo_de_ref(ref)].append(ref)

        modelo_max_dt_op = defaultdict(Max)
        ref_max_dt_op = referencias_com_op(cursor)
        for row in ref_max_dt_op:
            modelo_max_dt_op[row['modelo']].value = row['dt_digitacao']
        modelo_dt_op = {m: modelo_max_dt_op[m].value for m in modelo_max_dt_op}

        modelo_max_dt_venda = defaultdict(Max)
        ref_max_dt_venda = referencias_vendidas(cursor)
        for row in ref_max_dt_venda:
            modelo_max_dt_venda[row['modelo']].value = row['data_emissao']
        modelo_dt_venda = {m: modelo_max_dt_venda[m].value for m in modelo_max_dt_venda}

        dados = []
        for modelo in modelo_refs:
            dados.append({
                'modelo_int': modelo,
                'modelo': f"{modelo}",
                'ref': ", ".join(sorted(modelo_refs[modelo])),
                'op': modelo_dt_op[modelo].date() if modelo in modelo_dt_op else dt_old,
                'nf': modelo_dt_venda[modelo].date() if modelo in modelo_dt_venda else dt_old,
            })
        
        dados.sort(key=operator.itemgetter('modelo_int'))

        dados_op = dados.copy()
        dados_op.sort(key=operator.itemgetter('op'))

        dados_nf = dados.copy()
        dados_nf.sort(key=operator.itemgetter('nf'))

        for row in dados_op:
            if row['op'] == dt_old:
                row['op'] = 'Sem OP'
                if row['nf'] == dt_old:
                    row['|STYLE'] = "color: red;"
            if row['nf'] == dt_old:
                row['nf'] = 'Sem NF'

        self.context.update({
            'headers': [
                'Referências no sistema antigo',
                'Modelo',
                'Data da última OP do modelo',
                'Data da última venda do modelo',
            ],
            'fields': ['ref', 'modelo', 'op', 'nf'],
            'style': {2: 'text-align: center;'},
            'data': dados,
            'data_op': dados_op,
            'data_nf': dados_nf,
        })

    def get(self, request, *args, **kwargs):
        self.request = request
        self.mount_context()
        return render(request, self.template_name, self.context)

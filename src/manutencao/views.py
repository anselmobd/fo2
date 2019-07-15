from pprint import pprint
from datetime import date, timedelta

from django.views import View
from django.shortcuts import render
from django.db.models import Exists, OuterRef

from base.views import O2BaseGetView

import manutencao.models as models


def index(request):
    context = {}
    return render(request, 'manutencao/index.html', context)


class Rotinas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Rotinas, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/rotinas.html'
        self.title_name = 'Rotinas'

    def mount_context(self):
        if self.request.user.id is None:
            rotinas = models.Rotina.objects.all().order_by(
                'tipo_maquina', 'nome')
            if len(rotinas) == 0:
                self.context.update({
                    'msg_erro': 'Nenhuma rotina cadastrada',
                })
                return

            data = list(rotinas.values(
                'tipo_maquina__nome', 'frequencia__nome', 'nome'))

            self.context.update({
                'headers': ('Tipo de máquina', 'Frequência', 'Nome da rotina'),
                'fields': ('tipo_maquina__nome', 'frequencia__nome', 'nome'),
                'data': data,
            })
            return

        if self.request.user.is_superuser:
            utm = models.UsuarioTipoMaquina.objects.all()
        else:
            utm = models.UsuarioTipoMaquina.objects.filter(
                usuario=self.request.user)
        if len(utm) == 0:
            return

        mq = models.Maquina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id')).order_by('nome')
        if len(mq) == 0:
            return

        m_data = list(mq.values(
            'tipo_maquina__nome', 'nome', 'descricao', 'data_inicio'))
        self.context.update({
            'm_headers': ('Tipo de máquina', 'Nome', 'Descrição',
                          'Data de início'),
            'm_fields': ('tipo_maquina__nome', 'nome', 'descricao',
                         'data_inicio'),
            'm_data': m_data,
        })

        rot = models.Rotina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id')).order_by('-frequencia__ordem')
        if len(rot) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma rotina cadastrada para o usuário atual',
            })
            return
        # pprint(rot.values())
        # pprint(mq.values())
        domingo = date.today()-timedelta(days=date.today().weekday()+1)
        tamanho_periodo = timedelta(days=7)
        dia1 = timedelta(days=1)
        meses_nomes = ['Anterior', 'Atual', 'Próximo']
        meses = []
        dtini = domingo - tamanho_periodo
        for i in range(3):
            mes = {
                'ini': dtini,
                'fim': dtini + tamanho_periodo - dia1,
                'nome': meses_nomes[i],
                'r_headers': ('Máquina', 'Rotina', 'Data'),
                'r_fields': ('maquina', 'rotina', 'data'),
                'r_data': [],
            }
            meses.append(mes)
            dtini = dtini + tamanho_periodo
        # print(meses)

        def unidade_tempo2dias(unid):
            if unid == 's':
                return 7
            if unid == 'm':
                return 30
            if unid == 't':
                return 90
            if unid == 'e':
                return 180
            if unid == 'a':
                return 360
            return 1

        tem_rotina = False
        for mes in meses:
            # pprint(mes)
            for maquina in mq:
                # print('==== maquina', maquina)
                diasini = (mes['ini'] - maquina.data_inicio).days
                # print('diasini', diasini)
                diasfim = (mes['fim'] - maquina.data_inicio).days
                # print('diasfim', diasfim)
                for rotina in rot:
                    # print('== rotina', rotina)
                    dias_periodo = unidade_tempo2dias(
                        rotina.frequencia.unidade_tempo.codigo
                        ) * rotina.frequencia.qtd_tempo
                    # print('dias_periodo', dias_periodo)
                    periodos_ini = diasini // dias_periodo
                    # print('periodos_ini', periodos_ini)
                    modulo_ini = diasini % dias_periodo
                    # print('modulo_ini', modulo_ini)
                    periodos_fim = diasfim // dias_periodo
                    # print('periodos_fim', periodos_fim)
                    executa = False
                    if modulo_ini == 0 and periodos_ini > 0:
                        executa = True
                        data = maquina.data_inicio + timedelta(
                            days=periodos_ini*dias_periodo)
                    elif periodos_fim > 0 \
                            and periodos_ini != periodos_fim:
                        executa = True
                        data = maquina.data_inicio + timedelta(
                            days=periodos_fim*dias_periodo)
                    if executa:
                        # print('busca data', data)
                        tem_rotina = True
                        busca = [
                            m for m in mes['r_data']
                            if m['maquina'] == maquina and m['data'] == data
                        ]
                        if len(busca) == 0:
                            mes['r_data'].append({
                                'maquina': maquina,
                                'rotina': rotina,
                                'data': data
                            })
                            # print('executar data', data)

        if tem_rotina:
            for mes in meses:
                mes['r_data'] = sorted(mes['r_data'], key=lambda i: i['data'])
            self.context.update({
                'meses': meses,
            })

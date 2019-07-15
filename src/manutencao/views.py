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
            'tipo_maquina__id'))
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
        dias30 = timedelta(days=30)
        dia1 = timedelta(days=1)
        meses_nomes = ['Anterior', 'Atual', 'Próximo']
        meses = []
        dtini = domingo - dias30
        for i in range(3):
            mes = {
                'ini': dtini,
                'fim': dtini + dias30 - dia1,
                'fim_teste': dtini + dias30,
                'nome': meses_nomes[i],
                'r_headers': ('Máquina', 'Rotina', 'Data'),
                'r_fields': ('maquina', 'rotina', 'data'),
                'r_data': [],
            }
            meses.append(mes)
            dtini = dtini + dias30
        # print(meses)

        def unidade_tempo2dias(unid):
            if unid == 's':
                return 7
            if unid == 'm':
                return 30
            if unid == 't':
                return 91
            if unid == 'e':
                return 182
            if unid == 'a':
                return 365
            return 1

        tem_rotina = False
        for mes in meses:
            # pprint(mes)
            for maquina in mq:
                for rotina in rot:
                    # print(maquina)
                    # print(rotina)
                    diasini = (mes['ini'] - maquina.data_inicio).days
                    # print(diasini)
                    diasfim = (mes['fim_teste'] - maquina.data_inicio).days
                    # print(diasfim)
                    dias_periodo = unidade_tempo2dias(
                        rotina.frequencia.unidade_tempo.codigo
                        ) * rotina.frequencia.qtd_tempo
                    # print(dias_periodo)
                    periodos_ini = diasini // dias_periodo
                    # print(periodos_ini)
                    periodos_fim = diasfim // dias_periodo
                    # print(periodos_fim)
                    if periodos_fim > 0 and periodos_ini != periodos_fim:
                        tem_rotina = True
                        mes['r_data'].append({
                            'maquina': maquina,
                            'rotina': rotina,
                            'data': maquina.data_inicio + timedelta(
                                days=periodos_fim*dias_periodo)
                        })
                        # print('executar')
                        break
                    # else:
                        # print('não executar')

        if tem_rotina:
            self.context.update({
                'meses': meses,
            })

from pprint import pprint
from datetime import date, timedelta, datetime


from django.views import View
from django.shortcuts import render
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from base.views import O2BaseGetView

import manutencao.models as models


def index(request):
    context = {}
    return render(request, 'manutencao/index.html', context)


class Maquinas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Maquinas, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/maquinas.html'
        self.title_name = 'Máquinas'

    def mount_context(self):
        mq = models.Maquina.objects.all().order_by('nome')
        if len(mq) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma máquina cadastrada',
            })
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


class Rotinas(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Rotinas, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/rotinas.html'
        self.title_name = 'Rotinas'

    def mount_context(self):
        rotinas = models.Rotina.objects.all().order_by(
            'tipo_maquina', 'frequencia__ordem')
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


class Executar(LoginRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Executar, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/executar.html'
        self.title_name = 'Executar'

    def mount_context(self):
        if self.request.user.is_superuser:
            utm = models.UsuarioTipoMaquina.objects.all().distinct()
        else:
            utm = models.UsuarioTipoMaquina.objects.filter(
                usuario=self.request.user)
        if len(utm) == 0:
            self.context.update({
                'msg_erro': ('Nenhum tipo de máquina sob responsabilidade '
                             'de "{}"').format(self.request.user.username),
            })
            return

        m_data = list(utm.values('tipo_maquina__nome'))
        self.context.update({
            'm_fields': ('tipo_maquina__nome', ),
            'm_data': m_data,
        })

        mq = models.Maquina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id')).order_by('nome')
        if len(mq) == 0:
            self.context.update({
                'msg_erro': ('Nenhuma  máquina sob responsabilidade '
                             'de "{}"').format(self.request.user.username),
            })
            return

        rot = models.Rotina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id')).order_by('-frequencia__ordem')
        if len(rot) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma rotina cadastrada para o usuário atual',
            })
            return

        domingo = date.today()-timedelta(days=date.today().weekday()+1)
        tamanho_periodo = timedelta(days=7)
        dia1 = timedelta(days=1)
        meses_href = ['anterior', 'atual', 'proximo']
        meses_nomes = ['Anterior', 'Atual', 'Próximo']
        meses_ativa = [False, True, False]
        meses = []
        dtini = domingo - tamanho_periodo
        for i in range(3):
            mes = {
                'ini': dtini,
                'fim': dtini + tamanho_periodo - dia1,
                'nome': meses_nomes[i],
                'ativa': meses_ativa[i],
                'href': meses_href[i],
                'r_headers': ('Máquina', 'Rotina', 'Data'),
                'r_fields': ('maquina', 'rotina', 'data'),
                'r_data': [],
            }
            meses.append(mes)
            dtini = dtini + tamanho_periodo

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
            for maquina in mq:
                diasini = (mes['ini'] - maquina.data_inicio).days
                diasfim = (mes['fim'] - maquina.data_inicio).days
                for rotina in rot:
                    dias_periodo = unidade_tempo2dias(
                        rotina.frequencia.unidade_tempo.codigo
                        ) * rotina.frequencia.qtd_tempo
                    periodos_ini = diasini // dias_periodo
                    modulo_ini = diasini % dias_periodo
                    periodos_fim = diasfim // dias_periodo
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
                        tem_rotina = True
                        busca = [
                            m for m in mes['r_data']
                            if m['maquina'] == maquina and m['data'] == data
                        ]
                        if len(busca) == 0:
                            mes['r_data'].append({
                                'maquina': maquina,
                                'rotina': rotina,
                                'data': data,
                                'data|TARGET': '_BLANK',
                                'data|LINK': reverse(
                                    'manutencao:imprimir',
                                    args=[rotina.id, maquina.id, data])
                            })

        if tem_rotina:
            for mes in meses:
                mes['r_data'] = sorted(mes['r_data'], key=lambda i: i['data'])
            self.context.update({
                'meses': meses,
            })


class Imprimir(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Imprimir, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/imprimir.html'
        self.get_args = ['rotina', 'maquina', 'data']
        self.get_args2contect = True

    def mount_context(self):
        if self.request.user.id is None:
            return

        if self.request.user.is_superuser:
            utm = models.UsuarioTipoMaquina.objects.all()
        else:
            utm = models.UsuarioTipoMaquina.objects.filter(
                usuario=self.request.user)
        if len(utm) == 0:
            return

        dia = datetime.strptime(self.kwargs['data'], '%Y-%m-%d').date()

        mq = models.Maquina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id'), id=self.kwargs['maquina'])
        if len(mq) != 1:
            return
        data_m = list(mq.values(
            'tipo_maquina',
            'nome',
            'slug',
            'descricao',
            'data_inicio',
        ))[0]

        rot = models.Rotina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id'), id=self.kwargs['rotina'])
        if len(rot) != 1:
            return
        data_r = list(rot.values(
            'tipo_maquina',
            'tipo_maquina__nome',
            'frequencia',
            'frequencia__nome',
            'nome',
        ))[0]

        ativ = models.RotinaPasso.objects
        ativ = ativ.filter(rotina__in=rot)
        ativ = ativ.annotate(tem_medidas=Exists(
            models.AtividadeMetrica.objects.filter(
                atividade=OuterRef('atividade')
            )))
        ativ = ativ.order_by('ordem')
        data = list(ativ.values(
            'ordem',
            'atividade__id',
            'atividade__descricao',
            'rotina__nome',
            'rotina__frequencia__nome',
            'tem_medidas',
        ))

        ordem = 1
        for row in data:
            row['ordem'] = ordem
            ordem += 1
            metricas = models.AtividadeMetrica.objects.filter(
                atividade__id=row['atividade__id']
            ).order_by('ordem').values()
            row['metricas'] = metricas

        self.context.update({
            'data_m': data_m,
            'data_r': data_r,
            'data': data,
            'dia': dia,
            'now': datetime.now(),
        })

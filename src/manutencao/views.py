from datetime import date, timedelta, datetime
from pprint import pprint
# from weasyprint import HTML

from django.views import View
from django.shortcuts import render
# from django.http import HttpResponse
# from django.template.loader import render_to_string
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from base.views import O2BaseGetView
from utils.functions.date import dow_info
from utils.views import group_rowspan

import manutencao.models as models


def index(request):
    return render(request, 'manutencao/index.html')


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
            'id', 'tipo_maquina__nome', 'frequencia__nome', 'nome'))

        for row in data:
            row['nome|LINK'] = reverse(
                'manutencao:rotina__get', args=[row['id']])

        self.context.update({
            'headers': ('Tipo de máquina', 'Frequência', 'Nome da rotina'),
            'fields': ('tipo_maquina__nome', 'frequencia__nome', 'nome'),
            'data': data,
        })


class Rotina(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Rotina, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/rotina.html'
        self.title_name = 'Rotina'
        self.get_args = ['id']
        self.get_args2context = True

    def mount_context(self):
        ativ = models.RotinaPasso.objects
        ativ = ativ.filter(rotina__id=self.context['id'])
        ativ = ativ.annotate(tem_medidas=Exists(
            models.AtividadeMetrica.objects.filter(
                atividade=OuterRef('atividade')
            )))
        ativ = ativ.order_by('ordem')
        if len(ativ) != 0:
            data = list(ativ.values(
                'ordem',
                'atividade__id',
                'atividade__descricao',
                'rotina__nome',
                'rotina__frequencia__nome',
                'rotina__tipo_maquina__nome',
                'tem_medidas',
            ))

            self.context.update({
                'rotina':
                    ' "{} - {} - {}"'.format(
                        data[0]['rotina__tipo_maquina__nome'],
                        data[0]['rotina__frequencia__nome'],
                        data[0]['rotina__nome'],
                    ),
                'headers': ['Ordem', 'Atividade'],
                'fields': ['ordem', 'atividade__descricao'],
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
                'r_headers': ('Data', 'Dia', 'OS', 'Máquina', 'Rotina'),
                'r_fields': ('data', 'down', 'cria_os', 'maquina', 'rotina'),
                'r_data': [],
                'r_group': ['data', 'down']
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
                            if m['maquina'] == maquina
                        ]
                        if len(busca) == 0:
                            linha = {
                                'maquina': maquina,
                                'rotina': rotina,
                                'data': data,
                                'down': dow_info(data, 'name'),
                            }
                            try:
                                os = models.OS.objects.get(
                                    maquina=maquina,
                                    rotina=rotina,
                                    data_agendada=data,
                                )
                                linha.update({
                                    'cria_os': os.numero,
                                    'cria_os|TARGET': '_BLANK',
                                    'cria_os|GLYPHICON': 'glyphicon-print',
                                    'cria_os|LINK': reverse(
                                        'manutencao:imprimir',
                                        args=[rotina.id, maquina.id, data]),
                                })
                            except models.OS.DoesNotExist as e:
                                linha.update({
                                    'cria_os': 'Cria',
                                    'cria_os|TARGET': '_BLANK',
                                    'cria_os|GLYPHICON': 'glyphicon-plus',
                                    'cria_os|LINK': reverse(
                                        'manutencao:cria_os',
                                        args=[rotina.id, maquina.id, data]),
                                })
                            mes['r_data'].append(linha)

        if tem_rotina:
            for mes in meses:
                mes['r_data'] = sorted(mes['r_data'], key=lambda i: i['data'])
                group_rowspan(mes['r_data'], mes['r_group'])

            self.context.update({
                'meses': meses,
            })


def imprimir_mount_context(request, kwargs, context):
    if request.user.id is None:
        return

    if request.user.is_superuser:
        utm = models.UsuarioTipoMaquina.objects.all()
    else:
        utm = models.UsuarioTipoMaquina.objects.filter(
            usuario=request.user)
    if len(utm) == 0:
        return

    dia = datetime.strptime(kwargs['data'], '%Y-%m-%d').date()

    mq = models.Maquina.objects.filter(tipo_maquina__in=utm.values(
        'tipo_maquina__id'), id=kwargs['maquina'])
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
        'tipo_maquina__id'), id=kwargs['rotina'])
    if len(rot) != 1:
        return
    data_r = list(rot.values(
        'tipo_maquina',
        'tipo_maquina__nome',
        'frequencia',
        'frequencia__nome',
        'nome',
    ))[0]

    os = models.OS.objects.filter(
        maquina=mq,
        rotina=rot,
        data_agendada=dia,
    )
    if len(os) != 1:
        return
    data_os = list(os.values())[0]

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

    context.update({
        'data_m': data_m,
        'data_r': data_r,
        'data_os': data_os,
        'data': data,
        'dia': dia,
        'dow': dow_info(dia, 'name', True),
        'now': datetime.now(),
    })


class Imprimir(LoginRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Imprimir, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/imprimir.html'
        self.get_args = ['rotina', 'maquina', 'data']
        self.get_args2context = True

    # def my_render(self):
    #     html_rendered = render_to_string(self.template_name, self.context)
    #     html = HTML(string=html_rendered)
    #     html.write_pdf('/tmp/example.pdf')
    #     return HttpResponse(html_rendered)
    #     # return render(self.request, self.template_name, self.context)

    def mount_context(self):
        imprimir_mount_context(self.request, self.kwargs, self.context)


class CriaOS(LoginRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(CriaOS, self).__init__(*args, **kwargs)
        self.template_name = 'manutencao/imprimir.html'
        self.get_args = ['rotina', 'maquina', 'data']
        self.get_args2context = True

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
        mq = mq[0]

        rot = models.Rotina.objects.filter(tipo_maquina__in=utm.values(
            'tipo_maquina__id'), id=self.kwargs['rotina'])
        if len(rot) != 1:
            return
        rot = rot[0]

        try:
            os = models.OS.objects.get(
                maquina=mq,
                rotina=rot,
                data_agendada=dia,
            )
        except models.OS.DoesNotExist as e:
            os = models.OS()
            os.maquina = mq
            os.rotina = rot
            os.data_agendada = dia
            os.usuario = self.request.user
            os.save()

        imprimir_mount_context(self.request, self.kwargs, self.context)

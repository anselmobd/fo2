import datetime

from django.shortcuts import render
from django.views import View

from fo2.models import rows_to_dict_list

from .models import NotaFiscal
from .forms import NotafiscalRelForm


def index(request):
    context = {}
    return render(request, 'logistica/index.html', context)


class NotafiscalRel(View):
    Form_class = NotafiscalRelForm
    template_name = 'logistica/notafiscal_rel.html'
    title_name = 'Controle de data de saída de NF'

    def mount_context(self, form):
        # A ser produzido
        context = {}
        if form['data_ate'] is None:
            form['data_ate'] = form['data_de']

        select = NotaFiscal.objects
        if form['data_de']:
            select = select.filter(
                faturamento__date__gte=form['data_de']
                ).filter(
                faturamento__date__lte=form['data_ate']
                ).filter(natu_venda=True).filter(ativa=True)
            context.update({
                'data_de': form['data_de'],
                'data_ate': form['data_ate'],
            })
        if form['uf']:
            select = select.filter(uf=form['uf'])
            context.update({
                'uf': form['uf'],
            })
        if form['nf']:
            select = select.filter(numero=form['nf'])
            context.update({
                'nf': form['nf'],
            })
        select = select.order_by('numero')
        data = list(select.values())
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:
            for row in data:
                if row['saida'] is None:
                    row['saida'] = '-'
                if row['entrega'] is None:
                    row['entrega'] = '-'
                if row['confirmada']:
                    row['confirmada'] = 'S'
                else:
                    row['confirmada'] = 'N'
                if row['observacao'] is None:
                    row['observacao'] = ' '
            context.update({
                'headers': ('Número', 'Faturamento',
                            'Saida', 'Agendada', 'Entregue',
                            'UF', 'Cliente', 'Transportadora',
                            'Volumes', 'Valor', 'Observação'),
                'fields': ('numero', 'faturamento',
                           'saida', 'entrega', 'confirmada',
                           'uf', 'dest_nome', 'transp_nome',
                           'volumes', 'valor', 'observacao'),
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'dia' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'dia' in kwargs:
            data = '{dia}/{mes}/{ano}'.format(**kwargs)
            form.data['data_de'] = data
            form.data['data_ate'] = data
        if form.is_valid():
            context.update(self.mount_context(form.cleaned_data))
        context['form'] = form
        return render(request, self.template_name, context)

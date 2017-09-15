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

    def mount_context(self, data_de, data_ate):
        # A ser produzido
        context = {}
        if data_ate is None:
            data_ate = data_de
        context.update({
            'data_de': data_de,
            'data_ate': data_ate,
        })

        data = list(NotaFiscal.objects.filter(
            faturamento__date__gte=data_de
            ).filter(
            faturamento__date__lte=data_ate
            ).filter(natu_venda=True).filter(ativa=True).values())

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
        if 'data' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'data' in kwargs:
            form.data['data_de'] = kwargs['data']
            form.data['data_ate'] = kwargs['data']
        if form.is_valid():
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            context.update(self.mount_context(data_de, data_ate))
        context['form'] = form
        return render(request, self.template_name, context)

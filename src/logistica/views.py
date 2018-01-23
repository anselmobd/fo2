import datetime
from operator import itemgetter

from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.db.models import When, F, Q

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

    def mount_context(self, form, form_obj):
        # A ser produzido
        context = {}
        select = NotaFiscal.objects.filter(natu_venda=True).filter(ativa=True)
        if form['data_de']:
            select = select.filter(
                faturamento__date__gte=form['data_de']
                )
            context.update({
                'data_de': form['data_de'],
            })
        if form['data_ate']:
            select = select.filter(
                faturamento__date__lte=form['data_ate']
                )
            context.update({
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
        if form['cliente']:
            condition = Q(dest_nome__icontains=form['cliente']) | \
                        Q(dest_cnpj__contains=form['cliente'])
            select = select.filter(condition)
            context.update({
                'cliente': form['cliente'],
            })
        if form['transportadora']:
            condition = Q(transp_nome__icontains=form['transportadora'])
            select = select.filter(condition)
            context.update({
                'transportadora': form['transportadora'],
            })
        if form['data_saida'] != 'N':
            select = select.filter(saida__isnull=form['data_saida'] == 'S')
            context.update({
                'data_saida': [
                    ord[1] for ord in form_obj.fields['data_saida'].choices
                    if ord[0] == form['data_saida']][0],
            })

        select = select.order_by('-numero')
        data = list(select.values())
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:
            for row in data:
                if row['saida'] is None:
                    row['saida'] = '-'
                    row['atraso'] = (
                        timezone.now() - row['faturamento']).days
                else:
                    row['atraso'] = (
                        row['saida'] - row['faturamento'].date()).days
                if row['entrega'] is None:
                    row['entrega'] = '-'
                if row['confirmada']:
                    row['confirmada'] = 'S'
                else:
                    row['confirmada'] = 'N'
                if row['observacao'] is None:
                    row['observacao'] = ' '
                if row['ped_cliente'] is None:
                    row['ped_cliente'] = ' '
                row['atraso_order'] = -row['atraso']
            if form['ordem'] == 'A':
                data.sort(key=itemgetter('atraso_order'))
            context.update({
                'headers': ('Número', 'Faturamento', 'Atraso',
                            'Saida', 'Agendada', 'Entregue',
                            'UF', 'CNPJ', 'Cliente', 'Transportadora',
                            'Volumes', 'Valor', 'Observação',
                            'Pedido', 'Ped.Cliente'),
                'fields': ('numero', 'faturamento', 'atraso',
                           'saida', 'entrega', 'confirmada',
                           'uf', 'dest_cnpj', 'dest_nome', 'transp_nome',
                           'volumes', 'valor', 'observacao',
                           'pedido', 'ped_cliente'),
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
            context.update(self.mount_context(form.cleaned_data, form))
        context['form'] = form
        return render(request, self.template_name, context)

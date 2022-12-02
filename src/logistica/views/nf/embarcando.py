from pprint import pprint

from django.utils import timezone
from django.urls import reverse

from o2.views.base.get import O2BaseGetView

from logistica.models import NotaFiscal


class NotafiscalEmbarcando(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalEmbarcando, self).__init__(*args, **kwargs)
        self.template_name = 'logistica/notafiscal_embarcando.html'
        self.title_name = 'Notas fiscais entregues ao apoio'

    def mount_context(self):
        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]
        nfs = NotaFiscal.objects.filter(posicao_id=2).order_by('numero')
        data = list(nfs.values(*fields, 'posicao__nome'))
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma NF entregues ao apoio',
            })

        for row in data:
            row['numero|LINK'] = reverse(
                'logistica:notafiscal_numero', args=[row['numero']])
            row['numero|TARGET'] = '_BLANK'
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
            if row['natu_venda']:
                row['venda'] = 'Sim'
            else:
                row['venda'] = 'Não'
            if row['ativa']:
                row['ativa'] = 'Ativa'
            else:
                row['ativa'] = 'Cancelada'
            if row['nf_devolucao'] is None:
                row['nf_devolucao'] = 'Não'

        self.context.update({
            'headers': ('No.', 'Faturamento', 'Venda', 'Ativa',
                        'Devolvida', 'Posição',
                        'Atraso', 'Saída', 'Agendada',
                        'Entregue', 'UF', 'CNPJ', 'Cliente',
                        'Transp.', 'Vol.', 'Valor', 'Observação',
                        'Pedido', 'Ped.Cliente'),
            'fields': ('numero', 'faturamento', 'venda', 'ativa',
                       'nf_devolucao', 'posicao__nome',
                       'atraso', 'saida', 'entrega',
                       'confirmada', 'uf', 'dest_cnpj', 'dest_nome',
                       'transp_nome', 'volumes', 'valor', 'observacao',
                       'pedido', 'ped_cliente'),
            'data': data,
            'quant': len(data),
        })

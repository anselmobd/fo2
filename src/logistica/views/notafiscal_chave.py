from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from logistica.forms import *
from logistica.queries import get_nf_pela_chave


class NotafiscalChave(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalChave, self).__init__(*args, **kwargs)
        self.permission_required = 'logistica.can_beep_shipment'
        self.Form_class = NotafiscalChaveForm
        self.template_name = 'logistica/notafiscal_chave.html'
        self.title_name = 'Movimenta NF por chave'
        self.get_args = ['chave']

    def mount_context(self):
        self.context.update({
            'chave': self.form.cleaned_data['chave'],
        })
        cursor = db_cursor_so(self.request)
        data_nf = get_nf_pela_chave(cursor, self.form.cleaned_data['chave'])
        if len(data_nf) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:
            nf = data_nf[0]['NUM_NOTA_FISCAL']

            alt_action = [
                k for k in self.request.POST.keys() if k.startswith('alt_')]
            if alt_action:
                nota_fiscal = NotaFiscal.objects.get(numero=nf)

                num_action = alt_action[0].split('_')[1]
                try:
                    pos_carga_alt = PosicaoCargaAlteracao.objects.values().get(
                        id=num_action)
                except PosicaoCargaAlteracao.DoesNotExist:
                    pos_carga_alt = {'inicial_id': -1}

                if nota_fiscal.posicao_id == pos_carga_alt['inicial_id']:
                    self.context.update({
                        'alerta_acao': True,
                    })
                    if pos_carga_alt['efeito_id'] == 2:
                        nota_fiscal.saida = timezone.now()
                    elif pos_carga_alt['efeito_id'] == 3:
                        nota_fiscal.saida = None
                    elif pos_carga_alt['efeito_id'] == 4:
                        if nota_fiscal.entrega is None:
                            nota_fiscal.entrega = timezone.now()
                        nota_fiscal.confirmada = True
                    elif pos_carga_alt['efeito_id'] == 5:
                        nota_fiscal.confirmada = False
                    nota_fiscal.save()

                    nota_fiscal.posicao_id = pos_carga_alt['final_id']
                    nota_fiscal.save()

                    pca_log = PosicaoCargaAlteracaoLog(
                        numero=nf, user=self.request.user)
                    pca_log.inicial_id = pos_carga_alt['inicial_id']
                    pca_log.final_id = pos_carga_alt['final_id']
                    pca_log.saida = nota_fiscal.saida
                    pca_log.save()

            fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]
            row = NotaFiscal.objects.values(
                *fields, 'posicao__nome').get(numero=nf)

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
                status = 'ATIVA'
                row['ativa'] = 'Ativa'
            else:
                status = 'CANCELADA'
                row['ativa'] = 'Cancelada'
            if row['nf_devolucao'] is None:
                row['nf_devolucao'] = 'Não'
                nf_devolucao = ''
            else:
                nf_devolucao = row['nf_devolucao']
                status = 'DEVOLVIDA'

            acoes = []
            pos_alt = list(PosicaoCargaAlteracao.objects.filter(
                inicial_id=row['posicao_id']).order_by('-ordem').values())
            for alt in pos_alt:
                if (not alt['so_nfs_ativas']) or status == 'ATIVA':
                    acoes.append({
                        'name': 'alt_{}'.format(alt['id']),
                        'descr': alt['descricao'],
                    })

            self.context.update({
                'status': status,
                'nf': row['numero'],
                'nf_devolucao': nf_devolucao,
                'acoes': acoes,
                'posicao': row['posicao__nome'],
                'headers1': ('Faturamento', 'Venda', 'Ativa',
                             'Devolvida', 'Atraso',
                             'Saída', 'Agendada', 'Entregue',),
                'fields1': ('faturamento', 'venda', 'ativa',
                            'nf_devolucao', 'atraso',
                            'saida', 'entrega', 'confirmada'),
                'data1': [row],
                'headers2': ('UF', 'CNPJ', 'Cliente', 'Transp.',
                             'Vol.', 'Valor', 'Observação',
                             'Pedido', 'Ped.Cliente'),
                'fields2': ('uf', 'dest_cnpj', 'dest_nome', 'transp_nome',
                            'volumes', 'valor', 'observacao',
                            'pedido', 'ped_cliente'),
                'data2': [row],
            })

            datalog = list(
                PosicaoCargaAlteracaoLog.objects.filter(
                    numero=nf).order_by('-time').values(
                        'numero', 'time', 'user',
                        'inicial__nome', 'final__nome', 'saida')
            )
            for row in datalog:
                if row['saida'] is None:
                    row['saida'] = '-'
            self.context.update({
                'headerslog': ('Hora', 'Usuário',
                               'Posição inicial', 'Posição final',
                               'Data de saída'),
                'fieldslog': ('time', 'user',
                              'inicial__nome', 'final__nome',
                              'saida'),
                'datalog': datalog,
            })

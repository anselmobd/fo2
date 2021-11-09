from pprint import pprint

from django.utils import timezone
from django.urls import reverse
from django.db.models import Q

from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat

from logistica.models import PosicaoCargaAlteracaoLog
from logistica.forms import NfPosicaoForm


class NotafiscalMovimentadas(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalMovimentadas, self).__init__(*args, **kwargs)
        self.Form_class = NfPosicaoForm
        self.template_name = 'logistica/notafiscal_movimentadas.html'
        self.title_name = 'Notas fiscais movimentadas'

    def mount_context(self):
        data = self.form.cleaned_data['data']
        posicao = self.form.cleaned_data['posicao']

        if data is None and posicao is None:
            return

        if data is None:
            if posicao.id != 2:
                self.context.update({
                    'msg_erro': 'Sem data, '
                                'só pode pesquisar "Entregue ao apoio"'})
                return

        nfs_mov = PosicaoCargaAlteracaoLog.objects
        if data is not None:
            nfs_mov = nfs_mov.filter(time__contains=data)
        if posicao is not None:
            nfs_mov = nfs_mov.filter(
                Q(inicial=posicao) | Q(final=posicao))
        nfs_mov = nfs_mov.distinct().values()
        if len(nfs_mov) == 0:
            self.context.update({
                'msg_erro': 'Nenhum movimento de NF encontrado'})
            return

        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]

        passo_context = []
        if posicao is None:
            n_passos = 1
        else:
            n_passos = 2
        for passo in range(n_passos):
            nfs_mov = PosicaoCargaAlteracaoLog.objects
            if data is not None:
                nfs_mov = nfs_mov.filter(time__contains=data)
            if passo == 0:
                if posicao is None:
                    descr = ''
                else:
                    descr = ' para a posição selecionada'
                    nfs_mov = nfs_mov.filter(final=posicao)
            else:
                descr = ' para fora da posição selecionada'
                if posicao is not None:
                    nfs_mov = nfs_mov.filter(inicial=posicao)
            nfs_mov = nfs_mov.distinct().values()

            if len(nfs_mov) != 0:
                numeros = set()
                for log in nfs_mov:
                    numeros.add(log['numero'])

                nfs = NotaFiscal.objects
                if posicao is None:
                    nfs = nfs.filter(
                        numero__in=numeros).order_by('posicao__id', '-numero')
                else:
                    nfs = nfs.filter(posicao_id=posicao.id)
                    nfs = nfs.filter(numero__in=numeros).order_by('-numero')

                dados = list(nfs.values(*fields, 'posicao__nome'))

                for row in dados:
                    row['numero|LINK'] = reverse(
                        'logistica:notafiscal_nf', args=[row['numero']])
                    row['numero|TARGET'] = '_BLANK'
                    if row['saida'] is None:
                        row['saida'] = '-'
                        if row['faturamento'] is not None:
                            row['atraso'] = (
                                timezone.now() - row['faturamento']).days
                        else:
                            row['atraso'] = 999
                    else:
                        if row['faturamento'] is not None:
                            row['atraso'] = (
                                row['saida'] - row['faturamento'].date()).days
                        else:
                            row['atraso'] = 999
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

                passo_context.append({
                    'descr': descr,
                    'data': data,
                    'posicao': posicao,
                    'headers': ('No.', 'Faturamento', 'Venda', 'Ativa',
                                'Devolvida', 'Posição',
                                'Atraso', 'Saída', 'Agendada',
                                'Entregue', 'UF', 'Cliente',
                                'Transp.', 'Vol.', 'Valor',
                                'Pedido', 'Ped.Cliente'),
                    'fields': ('numero', 'faturamento', 'venda', 'ativa',
                               'nf_devolucao', 'posicao__nome',
                               'atraso', 'saida', 'entrega',
                               'confirmada', 'uf', 'dest_nome',
                               'transp_nome', 'volumes', 'valor',
                               'pedido', 'ped_cliente'),
                    'style': untuple_keys_concat({
                        tuple(range(1, 11)): 'text-align: center;',
                        (14, 15, 16, 17): 'text-align: right;',
                    }),
                    'dados': dados,
                    'quant': len(dados),
                })
        self.context.update({
            'passo_context': passo_context, })

from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.classes import TermalPrint
from utils.table_defs import TableDefs

import lotes.models

from logistica.forms.nf import NfForm
from logistica.queries.etiqueta_nf import get_dados_nf


class EtiquetaNf(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EtiquetaNf, self).__init__(*args, **kwargs)
        self.Form_class = NfForm
        self.template_name = 'logistica/etiqueta_nf.html'
        self.title_name = "Etiqueta de NF"
        self.cleaned_data2self = True

        self.init_defs()

    def init_defs(self):
        self.col_defs = TableDefs(
            {
                'remet_nome': ["Emissor"],
                'remet_cnpj': ["CNPJ"],
                'nf': ["NF"],
                'vols': ["Volumes", 'c'],
                'peso_tot': ["Peso Total"],
                'ped': ["Pedido Tussor"],
                'ped_cli': ["Pedido do cliente"],
                'transp_nome': ["Transportadora"],
                'cli_nome': ["Cliente"],
                'ende': ["Endereço"],
                'end_num': ["Número"],
                'end_compl': ["Complemento"],
                'end_bairro': ["Bairro"],
                'end_cid': ["Cidade"],
                'end_uf': ["UF"],
                'cli_cep': ["CEP"],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        dados_nf = get_dados_nf(cursor, self.nf)
        if len(dados_nf) == 0:
            self.context.update({
                'msg_erro': "NF não encontrada",
            })
            return
        row = dados_nf[0]
        
        vol_inicial_val = int(self.vol_inicial) if self.vol_inicial else 1
        vol_final_val = int(self.vol_final) if self.vol_final else row['vols']

        if not (1 <= vol_inicial_val <= row['vols']):
            self.context.update({
                'msg_erro': "Caixa inicial inválida",
            })
            return

        if not (vol_inicial_val <= vol_final_val <= row['vols']):
            self.context.update({
                'msg_erro': "Caixa final inválida",
            })
            return

        qtd_vols = vol_final_val - vol_inicial_val + 1

        self.context.update(self.col_defs.hfs_dict())
        self.context.update({
            'data': dados_nf,
            'qtd_vols': qtd_vols,
        })

        if 'print' not in self.request.POST:
            return
        
        slug_impresso = 'etiqueta-de-volumes-de-nf'
        try:
            impresso = lotes.models.Impresso.objects.get(
                slug=slug_impresso)
        except lotes.models.Impresso.DoesNotExist:
            self.context.update({
                'msg_erro': f"Impresso '{slug_impresso}' não cadastrado",
            })
            return

        try:
            usuario_impresso = lotes.models.UsuarioImpresso.objects.get(
                usuario=self.request.user, impresso=impresso)
        except lotes.models.UsuarioImpresso.DoesNotExist:
            self.context.update({
                'msg_erro': (
                    f"Impresso '{slug_impresso}' não cadastrado para o usuário '{self.request.user}'"
                ),
            })
            return

        teg = TermalPrint(
            usuario_impresso.impressora_termica.nome,
            file_dir=f"impresso/{slug_impresso}/%Y/%m"
        )
        teg.template(usuario_impresso.modelo.gabarito, '\r\n')
        teg.printer_start()
        try:
            for i in range(row['vols']):
                vol = i + 1
                if vol < vol_inicial_val or vol > vol_final_val:
                    continue
                row['empresa'] = "Tussor" if self.empresa == 1 else "Gavi"
                row['svol'] = f"{vol:04d}"
                row['svols'] = f"{row['vols']:04d}"
                peso = row['peso_tot']/row['vols']
                row['peso'] = f"{peso:7.2f}"
                row['nf_num9'] = f"{row['nf_num']:09d}"
                teg.context(row)
                try:
                    teg.printer_send()
                except Exception as e:
                    self.context.update({
                        'msg_erro': f"Erro ao imprimir <{e}>",
                    })
                    return
        except Exception as e:
            raise e
        finally:
            teg.printer_end()

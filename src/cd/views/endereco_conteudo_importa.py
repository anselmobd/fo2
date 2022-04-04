from pprint import pprint, pformat
from collections import OrderedDict

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.classes import TermalPrint

import lotes.models

from cd.forms.endereco import EnderecoImprimeForm
from cd.queries.endereco import (
    add_lote_in_endereco,
    lotes_em_endereco,
    lotes_em_palete,
    query_endereco,
)


class EnderecoImporta(PermissionRequiredMixin, O2BaseGetPostView):

    externos = {
        '2S0001': {'palete':'PLT0801', 'antigo': 'S036'},
        '2S0002': {'palete':'PLT0802', 'antigo': 'S222'},
        '2S0003': {'palete':'PLT0803', 'antigo': 'S218'},
        '2S0004': {'palete':'PLT0804', 'antigo': 'YC300'},
        '2S0005': {'palete':'PLT0805', 'antigo': 'Y312'},
        '2S0006': {'palete':'PLT0806', 'antigo': 'YA216'},
        '2S0007': {'palete':'PLT0807', 'antigo': 'S167'},
        '2S0008': {'palete':'PLT0808', 'antigo': 'YB123'},
        '2S0009': {'palete':'PLT0809', 'antigo': 'S162'},
        '2S0010': {'palete':'PLT0810', 'antigo': 'S148'},
        '2S0011': {'palete':'PLT0811', 'antigo': 'YA302'},
        '2S0012': {'palete':'PLT0812', 'antigo': 'YC116'},
        '2S0013': {'palete':'PLT0813', 'antigo': 'YC102'},
        '2S0014': {'palete':'PLT0814', 'antigo': 'S165'},
        '2S0015': {'palete':'PLT0815', 'antigo': 'YD315'},
        '2S0016': {'palete':'PLT0816', 'antigo': 'S166'},
        '2S0017': {'palete':'PLT0817', 'antigo': 'S043'},
        '2S0018': {'palete':'PLT0818', 'antigo': 'S163'},
        '2S0019': {'palete':'PLT0819', 'antigo': 'S153'},
        '2S0020': {'palete':'PLT0820', 'antigo': 'YC103'},
        '2S0021': {'palete':'PLT0821', 'antigo': 'S164'},
        '2S0022': {'palete':'PLT0822', 'antigo': 'S237'},
        '2S0023': {'palete':'PLT0823', 'antigo': 'S127'},
        '2S0024': {'palete':'PLT0824', 'antigo': 'y310'},
        '2S0025': {'palete':'PLT0825', 'antigo': 'S044'},
        '2S0026': {'palete':'PLT0826', 'antigo': 'S047'},
        '2S0027': {'palete':'PLT0827', 'antigo': 'S189'},
        '2S0028': {'palete':'PLT0828', 'antigo': 'S136'},
        '2S0029': {'palete':'PLT0829', 'antigo': 'YC104'},
        '2S0030': {'palete':'PLT0830', 'antigo': 'S052'},
        '2S0031': {'palete':'PLT0831', 'antigo': 'S070'},
        '2S0032': {'palete':'PLT0832', 'antigo': 'Y146'},
        '2S0033': {'palete':'PLT0833', 'antigo': 'YE215'},
        '2S0034': {'palete':'PLT0834', 'antigo': 'YC109'},
        '2S0035': {'palete':'PLT0835', 'antigo': 'S053'},
        '2S0036': {'palete':'PLT0836', 'antigo': 'S054'},
        '2S0037': {'palete':'PLT0837', 'antigo': 'YC123'},
        '2S0038': {'palete':'PLT0838', 'antigo': 'YC105'},
        '2S0039': {'palete':'PLT0839', 'antigo': 'Y373'},
        '2S0040': {'palete':'PLT0840', 'antigo': 'S055'},
        '2S0041': {'palete':'PLT0841', 'antigo': 'S051'},
        '2S0042': {'palete':'PLT0842', 'antigo': 'YC110'},
        '2S0043': {'palete':'PLT0843', 'antigo': 'yc121'},
        '2S0044': {'palete':'PLT0844', 'antigo': 'YC120'},
        '2S0045': {'palete':'PLT0845', 'antigo': 'YC122'},
        '2S0046': {'palete':'PLT0846', 'antigo': 'S236'},
        '2S0047': {'palete':'PLT0847', 'antigo': 'S046'},
        '2S0048': {'palete':'PLT0848', 'antigo': 'Y201'},
        '2S0049': {'palete':'PLT0849', 'antigo': 'YB127'},
        '2S0050': {'palete':'PLT0850', 'antigo': 'YC115'},
        '2S0051': {'palete':'PLT0851', 'antigo': 'S141'},
        '2S0052': {'palete':'PLT0852', 'antigo': 'S142'},
        '2S0053': {'palete':'PLT0853', 'antigo': 'S042'},
        '2S0054': {'palete':'PLT0854', 'antigo': 'YB120'},
        '2S0055': {'palete':'PLT0855', 'antigo': 'S244'},
        '2S0056': {'palete':'PLT0856', 'antigo': 'YC124'},
        '2S0057': {'palete':'PLT0857', 'antigo': 'S040'},
        '2S0058': {'palete':'PLT0858', 'antigo': 'S062'},
        '2S0059': {'palete':'PLT0859', 'antigo': 'S063'},
        '2S0060': {'palete':'PLT0860', 'antigo': 'S037'},
        '2S0061': {'palete':'PLT0861', 'antigo': 'S067'},
        '2S0062': {'palete':'PLT0862', 'antigo': 'S065'},
        '2S0063': {'palete':'PLT0863', 'antigo': 'YC118'},
        '2S0064': {'palete':'PLT0864', 'antigo': 'S242'},
        '2S0066': {'palete':'PLT0866', 'antigo': 'S073'},
        '2S0067': {'palete':'PLT0867', 'antigo': 'S059'},
        '2S0068': {'palete':'PLT0868', 'antigo': 'S061'},
        '2S0069': {'palete':'PLT0869', 'antigo': 'YC127'},
        '2S0070': {'palete':'PLT0870', 'antigo': 'S137'},
        '2S0071': {'palete':'PLT0871', 'antigo': 'S050'},
        '2S0072': {'palete':'PLT0872', 'antigo': 'S041'},
        '2S0073': {'palete':'PLT0873', 'antigo': 'S060'},
        '2S0074': {'palete':'PLT0874', 'antigo': 'S064'},
        '2S0075': {'palete':'PLT0875', 'antigo': 'YB122'},
        '2S0076': {'palete':'PLT0876', 'antigo': 'S039'},
        '2S0077': {'palete':'PLT0877', 'antigo': 'S049'},
        '2S0078': {'palete':'PLT0878', 'antigo': 'S058'},
        '2S0079': {'palete':'PLT0879', 'antigo': 'S057'},
        '2S0080': {'palete':'PLT0880', 'antigo': 'YC107'},
        '2S0081': {'palete':'PLT0881', 'antigo': 'S126'},
        '2S0082': {'palete':'PLT0882', 'antigo': 'S069'},
        '2S0083': {'palete':'PLT0883', 'antigo': 'S068'},
        '2S0084': {'palete':'PLT0884', 'antigo': 'YC108'},
        '2S0085': {'palete':'PLT0885', 'antigo': 'Y322'},
        '2S0086': {'palete':'PLT0886', 'antigo': 'S056'},
        '2S0087': {'palete':'PLT0887', 'antigo': 'S071'},
        '2S0088': {'palete':'PLT0888', 'antigo': 'Y470'},
        '2S0089': {'palete':'PLT0889', 'antigo': 'Y456'},
        '2S0090': {'palete':'PLT0890', 'antigo': 'YB108'},
        '2S0091': {'palete':'PLT0891', 'antigo': 'S232'},
        '2S0092': {'palete':'PLT0892', 'antigo': 'Y460'},
        '2S0093': {'palete':'PLT0893', 'antigo': 'Y448'},
        '2S0094': {'palete':'PLT0894', 'antigo': 'Y473'},
        '2S0095': {'palete':'PLT0895', 'antigo': 'YC119'},
        '2S0096': {'palete':'PLT0896', 'antigo': 'S241'},
        '2S0097': {'palete':'PLT0897', 'antigo': 'S238'},
        '2S0098': {'palete':'PLT0898', 'antigo': 'S224'},
        '2S0099': {'palete':'PLT0899', 'antigo': 'YC114'},
        '2S0100': {'palete':'PLT0900', 'antigo': 'Y464'},
        '2S0101': {'palete':'PLT0901', 'antigo': 'YB118'},
        '2S0102': {'palete':'PLT0902', 'antigo': 'S138'},
        '2S0103': {'palete':'PLT0903', 'antigo': 'S151'},
        '2S0104': {'palete':'PLT0904', 'antigo': 'S135'},
        '2S0105': {'palete':'PLT0905', 'antigo': 'S145'},
        '2S0106': {'palete':'PLT0906', 'antigo': 'YB115'},
        '2S0107': {'palete':'PLT0907', 'antigo': 'S223'},
        '2S0108': {'palete':'PLT0908', 'antigo': 'YB106'},
        '2S0109': {'palete':'PLT0909', 'antigo': 'YB110'},
        '2S0110': {'palete':'PLT0910', 'antigo': 'YB105'},
        '2S0111': {'palete':'PLT0911', 'antigo': 'S140'},
        '2S0112': {'palete':'PLT0912', 'antigo': 'YB103'},
        '2S0113': {'palete':'PLT0913', 'antigo': 'YB104'},
        '2S0115': {'palete':'PLT0915', 'antigo': 'S038'},
        '2S0116': {'palete':'PLT0916', 'antigo': 'YB100'},
        '2S0117': {'palete':'PLT0917', 'antigo': 'YB101'},
        '2S0118': {'palete':'PLT0918', 'antigo': 'YB124'},
        '2S0119': {'palete':'PLT0919', 'antigo': 'YB125'},
        '2S0120': {'palete':'PLT0920', 'antigo': 'YB121'},
        '2S0121': {'palete':'PLT0921', 'antigo': 'YB116'},
        '2S0122': {'palete':'PLT0922', 'antigo': 'YB119'},
        '2S0123': {'palete':'PLT0923', 'antigo': 'S146'},
        '2S0124': {'palete':'PLT0924', 'antigo': 'YB109'},
        '2S0125': {'palete':'PLT0925', 'antigo': 'S233'},
        '2S0126': {'palete':'PLT0926', 'antigo': 'S144'},
        '2S0127': {'palete':'PLT0927', 'antigo': 'YC126'},
        '2S0128': {'palete':'PLT0928', 'antigo': 'S240'},
        '2S0129': {'palete':'PLT0929', 'antigo': 'S147'},
        '2S0130': {'palete':'PLT0930', 'antigo': 'S243'},
        '2S0131': {'palete':'PLT0931', 'antigo': 'S143'},
        '2S0132': {'palete':'PLT0932', 'antigo': 'S235'},
        '2S0133': {'palete':'PLT0933', 'antigo': 'YB107'},
        '2S0134': {'palete':'PLT0934', 'antigo': 'S225'},
        '2S0135': {'palete':'PLT0935', 'antigo': 'Y444'},
        '2S0136': {'palete':'PLT0936', 'antigo': 'YB126'},
        '2S0137': {'palete':'PLT0937', 'antigo': 'Y440'},
        '2S0138': {'palete':'PLT0938', 'antigo': 'YC117'},
        '2S0139': {'palete':'PLT0939', 'antigo': 'Y320'},
        '2S0140': {'palete':'PLT0940', 'antigo': 's168'},
        '2S0141': {'palete':'PLT0941', 'antigo': 'S228'},
        '2S0142': {'palete':'PLT0942', 'antigo': 'S230'},
        '2S0143': {'palete':'PLT0943', 'antigo': 'Y433'},
        '2S0144': {'palete':'PLT0944', 'antigo': 'S227'},
        '2S0145': {'palete':'PLT0945', 'antigo': 'Y101'},
        '2S0146': {'palete':'PLT0946', 'antigo': 'S231'},
        '2S0147': {'palete':'PLT0947', 'antigo': 'S229'},
        '2S0148': {'palete':'PLT0948', 'antigo': 'Y327'},
        '2S0149': {'palete':'PLT0949', 'antigo': 'Y435'},
        '2S0150': {'palete':'PLT0950', 'antigo': 'S226'},
        '2S0151': {'palete':'PLT0951', 'antigo': 'S234'},
        '2S0152': {'palete':'PLT0952', 'antigo': 'Y147'},
        '2S0153': {'palete':'PLT0953', 'antigo': 'Y114'},
        '2S0154': {'palete':'PLT0954', 'antigo': 'Y442'},
    }

    def __init__(self, *args, **kwargs):
        super(EnderecoImporta, self).__init__(*args, **kwargs)
        self.Form_class = EnderecoImprimeForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.permission_required = 'cd.can_admin_pallet'
        self.template_name = 'cd/endereco_conteudo_importa.html'
        self.title_name = 'Importa conteudo de endereços'
        self.cleaned_data2self = True

    def end_novo_para_antigo(self, endereco):
        if endereco[1] in 'ABCEFGH':
            return endereco[1]+endereco[3:]
        elif endereco[1] == 'D':
            andar = int(endereco[2:4])
            coluna = int(endereco[4:6])
            if coluna > 22:
                coluna -= 4
            elif coluna > 14:
                coluna -= 3
            elif coluna > 6:
                coluna -= 1
            return f'1D{andar:1}{coluna:02}'
        elif endereco[1] == 'L':
            return endereco[1:2]+'B'+endereco[3:]
        elif endereco[1] == 'Q':
            return endereco[1:2]+'A'+endereco[3:]
        elif endereco[1] == 'S':
            return (
                self.externos[endereco]['antigo']
                if endereco in self.externos
                else None
            )

    def lotes_end_apoio(self, endereco):
        data_rec = lotes.models.Lote.objects
        data_rec = data_rec.filter(local=endereco)
        data_rec = data_rec.order_by('op', 'lote')
        data = data_rec.values('op', 'lote')
        return list(data)

    def row_exist(self, row_a):
        for row_s in self.lotes_s:
            if (
                row_s['op'] == row_a['op'] and
                row_s['lote'] == row_a['lote']
            ):
                return True
        return False

    def importa_end(self, endereco):
        if endereco[1] == 'S':
            palete = (
                self.externos[endereco]['palete']
                if endereco in self.externos
                else None
            )
            self.lotes_s = lotes_em_palete(self.cursor, palete)
        else:
            self.lotes_s = lotes_em_endereco(self.cursor, endereco)
            palete = self.lotes_s[0]['palete']
        print(endereco)
        pprint(self.lotes_s)

        end_antigo = self.end_novo_para_antigo(
            endereco)
        print(end_antigo)

        if not palete:
            return {endereco: 'sem palete'}

        if not end_antigo:
            return {endereco: 'sem endereço antigo'}

        # return {endereco: 'debug'}
        
        lotes_a = self.lotes_end_apoio(end_antigo)
        pprint(lotes_a)

        result = {}
        for row_a in lotes_a:
            if not self.row_exist(row_a):
                print('inclui em', palete)
                pprint(row_a)
                if add_lote_in_endereco(
                    self.cursor,
                    palete,
                    row_a['op'],
                    row_a['lote'],
                ):
                    key = 'OK'
                else:
                    key = 'ERRO'
                try:
                    result[key].append(row_a['lote'])
                except Exception:
                    result[key] = [row_a['lote']]
                # break
                
        return {endereco: result}

    def importa(self):
        result = OrderedDict()
        for row in self.data[self.primeiro:self.ultimo+1]:
            result.update(
                self.importa_end(row['end'])
            )
        self.context.update({
            'mensagem': 'Processado',
            'log': pformat(result),
        })

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        self.inicial = self.inicial.upper()
        self.final = self.final.upper()

        self.data = query_endereco(self.cursor, 'TO')
        pprint(self.data[:2])

        self.primeiro = next(
            (
                idx for idx, row in enumerate(self.data)
                if row['end'] == self.inicial
            )
            , None
        )
        pprint(self.primeiro)
        if self.primeiro is None:
            self.context.update({
                'mensagem': 'Endereço inicial não existe',
            })
            return

        self.ultimo = next(
            (
                idx for idx, row in enumerate(self.data)
                if row['end'] == self.final
            )
            , None
        )
        pprint(self.ultimo)
        if self.ultimo is None:
            self.context.update({
                'mensagem': 'Endereço final não existe',
            })
            return

        if self.ultimo < self.primeiro:
            self.context.update({
                'mensagem': 'Endereço final anterior ao inicial',
            })
            return

        self.importa()

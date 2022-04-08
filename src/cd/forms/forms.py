import datetime
from pprint import pprint

from django import forms
from django.conf import settings
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce

from fo2.connections import db_cursor_so

from utils.functions.digits import fo2_digit_valid
from utils.functions.strings import only_digits

import lotes.models
import lotes.queries.lote


class RearrumarForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = [
            ('RAB', 'Rua AB (estantes A e B)'),
            ('RCD', 'Rua CD (estantes C e D)'),
            ('REF', 'Rua EF (estantes E e F)'),
            ('RGH', 'Rua GH (estantes G e H)'),
        ]
        self.fields['rua'] = forms.ChoiceField(
            choices=CHOICES,
            initial='RAB',
        )

        self.fields['endereco'] = forms.CharField(
            label='Endereço', min_length=2, max_length=9,
            widget=forms.TextInput(
                attrs={'autofocus': 'autofocus', 'size': 9}))

        self.fields['valid_rua'] = forms.CharField(
            required=False, widget=forms.HiddenInput())

        self.fields['valid_endereco'] = forms.CharField(
            required=False, widget=forms.HiddenInput())

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data

        if not endereco[0].isalpha():
            raise forms.ValidationError(
                "Deve iniciar com uma letra.")

        if not endereco[2:].isdigit():
            raise forms.ValidationError(
                "Depois de 1 ou 2 letras iniciais deve ter apenas números.")

        lotes_no_local = lotes.models.Lote.objects.filter(
            local=endereco).count()
        if lotes_no_local == 0:
            raise forms.ValidationError(
                f'O endereço "{endereco}" está vazio.')

        return endereco


class LoteForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', min_length=2, max_length=5,
        widget=forms.TextInput())
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    end_conf = forms.CharField(
        required=False,
        widget=forms.HiddenInput())
    identificado = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if endereco != "SAI":
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "Deve iniciar com uma letra.")
            if not endereco[2:].isdigit():
                raise forms.ValidationError(
                    "Depois de 1 ou 2 letras iniciais deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco


class EnderecarForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', min_length=2, max_length=5,
        widget=forms.TextInput(attrs={'size': 5}))
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(
            attrs={'type': 'number', 'size': 9, 'autofocus': 'autofocus'}))
    end_conf = forms.CharField(
        required=False,
        widget=forms.HiddenInput())
    identificado = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EnderecarForm, self).__init__(*args, **kwargs)

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if not endereco[0].isalpha():
            raise forms.ValidationError(
                "Deve iniciar com uma letra.")
        if not endereco[2:].isdigit():
            raise forms.ValidationError(
                "Depois de 1 ou 2 letras iniciais deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco

    def clean_lote(self):
        lote = only_digits(self.cleaned_data.get('lote', ''))

        cursor = db_cursor_so(self.request)
        periodo = lote[:4]
        ordem_confeccao = lote[-5:]
        lote_sys = lotes.queries.lote.existe_lote(
            cursor, periodo, ordem_confeccao)
        if len(lote_sys) == 0:
            raise forms.ValidationError("Lote não encontrado no Systêxtil")

        try:
            self.lote_record = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            raise forms.ValidationError("Lote não encontrado no Apoio")

        return lote


class RetirarForm(forms.Form):
    _tipo_retirada = 'total'

    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 9,
                               'autofocus': 'autofocus'}))

    identificado = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    def clean_lote(self):
        lote = only_digits(self.cleaned_data.get('lote', ''))

        try:
            self.lote_object = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            raise forms.ValidationError("Lote não encontrado")

        if self.lote_object.local is None:
            raise forms.ValidationError("Lote não endereçado")

        try:
            self.op_object = lotes.models.Op.objects.get(
                op=self.lote_object.op)
        except lotes.models.Op.DoesNotExist:
            raise forms.ValidationError("OP do lote não encontrada")

        slqs = lotes.models.SolicitaLoteQtd.objects.filter(
            lote=self.lote_object
        ).values(
            'solicitacao__coleta',
            'lote__qtd',
        ).annotate(
            qtdsum=Sum('qtd')
        )

        if len(slqs) == 0:
            if self.op_object.pedido != 0:
                return lote

            ende = self.lote_object.local
            rua = ''.join(filter(str.isalpha, ende))
            try:
                lotes.models.EnderecoDisponivel.objects.get(inicio=rua, disponivel=True) 
            except lotes.models.EnderecoDisponivel.DoesNotExist:
                # rua não válida -> permite retirar
                return lote

            try:
                lotes.models.EnderecoDisponivel.objects.get(inicio=ende, disponivel=False) 
                # endereço é inválido -> permite retirar
                return lote
            except lotes.models.EnderecoDisponivel.DoesNotExist:
                pass


            # rua válida e endereço não é inválido -> só retira com solicitação
            raise forms.ValidationError(
                "Lote não consta em nenhuma solicitação")

        slq = slqs[0]
        if self._tipo_retirada == 'total':
            if slq['qtdsum'] != slq['lote__qtd']:
                raise forms.ValidationError(
                    "Solicitação não é de total disponível")

        if not slq['solicitacao__coleta']:
            raise forms.ValidationError(
                "Coleta no CD não liberada")

        return lote

    def clean(self):
        data = self.data.copy()
        self.data = data


class RetirarParcialForm(forms.Form):
    _tipo_retirada = 'parcial'

    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 9,
                               'autofocus': 'autofocus'}))

    quant = forms.IntegerField(
        label='Qtd. peças', min_value=1,
        widget=forms.TextInput(attrs={'type': 'number', 'size': 4}))

    identificado = forms.CharField(
        required=False,
        widget=forms.HiddenInput())

    clean_lote = RetirarForm.clean_lote

    def clean(self):
        if not self.errors:
            cleaned_data = super().clean()
            quant = cleaned_data.get('quant', 0)

            # if quant == self.lote_record.qtd:
            #     self.add_error(
            #         'quant',
            #         "Quantidade igual à disponível. "
            #         "Faça uma retirada de lote inteiro"
            #     )

            if quant > self.lote_object.qtd:
                self.add_error(
                    "quant",
                    "Quantidade maior que a disponível"
                )

        # copiado para não ser immutable
        data = self.data.copy()
        self.data = data


class TrocaLocalForm(forms.Form):
    endereco_de = forms.CharField(
        label='Endereço antigo', min_length=2, max_length=5,
        widget=forms.TextInput())
    endereco_para = forms.CharField(
        label='Endereço novo', min_length=2, max_length=5,
        widget=forms.TextInput())

    identificado_de = forms.CharField(
        label='identificado de', required=False,
        widget=forms.HiddenInput())
    identificado_para = forms.CharField(
        label='identificado para', required=False,
        widget=forms.HiddenInput())

    def clean_endereco(self, campo):
        endereco = self.cleaned_data[campo].upper()
        data = self.data.copy()
        data[campo] = endereco
        self.data = data
        return endereco

    def valid_endereco(self, nome, endereco, sai=''):
        if endereco != sai:
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "O endereço {} deve iniciar com uma letra.".format(nome))
            if not (endereco[1:].isdigit() or endereco[1] == '%'):
                raise forms.ValidationError(
                    "No endereço {}, depois da letra inicial deve ter apenas "
                    "números.".format(nome))

    def clean_endereco_de(self):
        return self.clean_endereco('endereco_de')

    def clean_endereco_para(self):
        return self.clean_endereco('endereco_para')

    def clean(self):
        cleaned_data = super(TrocaLocalForm, self).clean()
        self.valid_endereco('antigo', cleaned_data['endereco_de'])
        self.valid_endereco('novo', cleaned_data['endereco_para'], 'SAI')
        if cleaned_data['endereco_de'][1] == "%" and \
                cleaned_data['endereco_para'] != 'SAI':
            raise forms.ValidationError(
                "O endereço antigo só pode indicar uma rua interira se "
                "endereço novo for 'SAI'.")
        if cleaned_data['endereco_de'] == cleaned_data['endereco_para']:
            raise forms.ValidationError(
                "Os endereços devem ser diferentes.")
        return cleaned_data


class TrocaEnderecoForm(forms.Form):
    endereco_de = forms.CharField(
        label='Endereço antigo', min_length=2, max_length=5,
        widget=forms.TextInput(attrs={'size': 5}))
    endereco_para = forms.CharField(
        label='Endereço novo', min_length=2, max_length=5,
        widget=forms.TextInput(attrs={'size': 5}))

    identificado_de = forms.CharField(
        label='identificado de', required=False,
        widget=forms.HiddenInput())
    identificado_para = forms.CharField(
        label='identificado para', required=False,
        widget=forms.HiddenInput())

    def clean_endereco(self, campo):
        endereco = self.cleaned_data[campo].upper()
        data = self.data.copy()
        data[campo] = endereco
        self.data = data
        return endereco

    def valid_endereco(self, nome, endereco):
        if not endereco[0].isalpha():
            raise forms.ValidationError(
                "O endereço {} deve iniciar com uma letra.".format(nome))
        if not endereco[1:].isdigit():
            raise forms.ValidationError(
                "No endereço {}, depois da letra inicial deve ter apenas "
                "números.".format(nome))

    def clean_endereco_de(self):
        return self.clean_endereco('endereco_de')

    def clean_endereco_para(self):
        return self.clean_endereco('endereco_para')

    def clean(self):
        cleaned_data = super(TrocaEnderecoForm, self).clean()
        self.valid_endereco('antigo', cleaned_data['endereco_de'])
        self.valid_endereco('novo', cleaned_data['endereco_para'])
        if cleaned_data['endereco_de'] == cleaned_data['endereco_para']:
            raise forms.ValidationError(
                "Os endereços devem ser diferentes.")
        return cleaned_data


class EstoqueForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', required=False, min_length=2, max_length=5,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    lote = forms.CharField(
        label='Lote', required=False, min_length=9, max_length=9,
        widget=forms.TextInput(attrs={'type': 'number'}))
    op = forms.CharField(
        label='OP', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    ref = forms.CharField(
        label='Referência', required=False, min_length=5, max_length=5,
        widget=forms.TextInput(attrs={'type': 'string'}))
    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False, min_length=1, max_length=6,
        widget=forms.TextInput(attrs={'type': 'string'}))
    data_de = forms.DateField(
        label='Data inicial', required=False,
        help_text='(Data de bipagem)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Data final', required=False,
        help_text='(Se não informar, assume igual a inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    CHOICES = [('B', 'Hora de bipagem'),
               ('O', 'OP Referência Cor Tamanho Endereço Lote'),
               ('R', 'Referência Cor Tamanho Endereço OP Lote'),
               ('E', 'Endereço OP Referência Cor Tamanho Lote')]
    ordem = forms.ChoiceField(
        label='Ordenação', choices=CHOICES, initial='B')
    SOLICITACAO_CHOICES = [
        ('N', 'Todos os lotes'),
        ('S', 'Sem solicitações'),
        ('P', 'Parcialmente solicitado'),
        ('I', 'Inteiramente solicitado'),
    ]
    solicitacao = forms.ChoiceField(
        label='Solicitação', choices=SOLICITACAO_CHOICES, initial='N')
    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if endereco and endereco not in ['RAB', 'RC', 'RDE', 'RFG']:
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "Deve iniciar com uma letra.")
            if not endereco[2:].isdigit():
                raise forms.ValidationError(
                    "Depois de 1 ou 2 letras iniciais deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        if cor:
            cor = cor.zfill(6)
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class ConfereForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', required=False, min_length=1, max_length=5,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if endereco:
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "Deve iniciar com uma letra.")
            if len(endereco) > 1:
                if not endereco[2:].isdigit():
                    raise forms.ValidationError(
                        "Depois de 1 ou 2 letras iniciais deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco


class SolicitacaoForm(forms.Form):
    codigo = forms.CharField(
        label='Código', max_length=20, min_length=1,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    descricao = forms.CharField(
        label='Descrição', required=False,
        widget=forms.TextInput(attrs={'size': 60}))
    pedidos = forms.CharField(
        required=False,
        help_text='(separados apenas por espaço)',
        widget=forms.TextInput(attrs={'size': 80}))
    data = forms.DateField(
        label='Data do embarque', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    ativa = forms.BooleanField(
        label='Ativa para o usuário', required=False)
    concluida = forms.BooleanField(
        label='Solicitação concluída', required=False)
    can_print = forms.BooleanField(
        label='Pode imprimir', required=False)
    coleta = forms.BooleanField(
        label='Pode coletar no CD', required=False)


class FiltraSolicitacaoForm(forms.Form):
    filtro = forms.CharField(
        max_length=20, min_length=1, required=False,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    data_de = forms.DateField(
        label='Data do embarque', required=False,
        help_text="(Data única ou início de período)",
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Data do embarque (final de período)', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    ref = forms.CharField(
        label='Referência', required=False, max_length=5,
        widget=forms.TextInput(
            attrs={'type': 'string', 'size': 5}))
    CHOICES = [
        ('dz', 'Diferente de zero'),
        ('nf', 'Não filtra'),
        ('iz', 'Igual a zero'),
    ]
    qtdcd = forms.ChoiceField(
        label='Qtd. no CD', choices=CHOICES, initial='dz')
    pagina = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class AskLoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(
            attrs={'type': 'number', 'autofocus': 'autofocus', 'size': 9}
        )
    )


class AskReferenciaForm(forms.Form):
    ref = forms.CharField(
        label='Filtro', required=False, max_length=5,
        help_text='(referência, com 5 caracteres, '
                  'ou parte numérica da referência ou vazio)',
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class HistoricoForm(forms.Form):
    op = forms.CharField(
        label='OP', required=True,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class ALoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class EtiquetasSolicitacoesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero'] = forms.CharField(
            label='Número de solicitação', required=True,
            widget=forms.TextInput(
                attrs={'type': 'number',
                       'min': '1',
                       'max': '9999999',
                       'size': '7',
                       'autofocus': 'autofocus'}))

        self.fields['selecao'] = forms.CharField(
            label='Seleção de etiquetas a imprimir', required=False,
            max_length=20,
            help_text="'' ou '20' ou '-5' ou '10-' ou '5-10' ou '5-10, 15'")

        self.fields['buscado_numero'] = forms.CharField(
            required=False, widget=forms.HiddenInput())

    def clean_numero(self):
        numero = self.cleaned_data.get('numero', '')

        if not fo2_digit_valid(numero):
            raise forms.ValidationError("Número inválido")

        try:
            solicitacao = lotes.models.SolicitaLote.objects.get(
                id=numero[:-2])
        except lotes.models.SolicitaLote.DoesNotExist:
            raise forms.ValidationError("Solicitação não existe")

        if settings.DESLIGANDO_CD_FASE >= 1:
            if solicitacao.create_at > datetime.datetime(2022, 2, 1, 18, 0, 0):
                raise forms.ValidationError("Solicitação criada depois de 01/02/2022 18h00.")

        solicitacao_prt = lotes.models.SolicitaLotePrinted.objects.filter(
            solicitacao=solicitacao
        )
        if len(solicitacao_prt) != 0:
            if not solicitacao.can_print:
                raise forms.ValidationError("Etiquetas já foram impressas")

        parciais = lotes.models.SolicitaLoteQtd.objects.values(
            'lote__op', 'lote__lote', 'lote__qtd_produzir',
            'lote__referencia', 'lote__cor', 'lote__tamanho'
        ).annotate(
            qtdsum=Sum('qtd')
        ).filter(
            solicitacao=solicitacao,
        ).exclude(
            lote__qtd_produzir=F('qtdsum'),
        )

        if len(parciais) == 0:
            raise forms.ValidationError("Sem lotes parciais")

        return numero


class AtividadeCDForm(forms.Form):
    data_de = forms.DateField(
        label='Data inicial', required=True,
        help_text='(Data de bipagem)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Data final', required=False,
        help_text='(Se não informar, assume igual a inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    CHOICES = [
        ('l', 'Listagem'),
        ('d', 'Data'),
        # ('du', 'Data, Usuário'),
        # ('ud', 'Usuário, Data'),
    ]
    apresentacao = forms.ChoiceField(
        label='Apresentação', choices=CHOICES, initial='d')


class ConteudoLocalForm(forms.Form):
    codigo = forms.CharField(
        label='End. ou Palete', min_length=6, max_length=8,
        widget=forms.TextInput(
            attrs={
                'size': 8,
                'autofocus': 'autofocus',
                'style': 'text-transform:uppercase;',
            }
        )
    )


class LocalizaLoteForm(forms.Form):
    lote = forms.CharField(
        min_length=9, max_length=9,
        widget=forms.TextInput(
            attrs={
                'size': 9,
                'type': 'number',
                'autofocus': 'autofocus',
            }
        )
    )


class ZeraPaleteForm(forms.Form):
    palete = forms.CharField(
        min_length=8, max_length=8,
        widget=forms.TextInput(
            attrs={
                'size': 8,
                'autofocus': 'autofocus',
                'style': 'text-transform:uppercase;',
            }
        )
    )
    identificado = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

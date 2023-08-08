import datetime
from pprint import pprint

from django import forms
from django.conf import settings
from django.db.models import F, Sum

from fo2.connections import db_cursor_so
from lotes.models.inventario import Inventario

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.digits import fo2_digit_valid
from utils.functions.strings import only_digits

from systextil.models import Colecao

import lotes.models
import lotes.queries.lote
from comercial.queries import get_tabela_preco
from lotes.models import Inventario
from lotes.models.inventario import (
    Inventario,
    InventarioLote,
)


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


class AtividadeCD63Form(forms.Form):
    data_de = forms.DateField(
        label='Data inicial', required=True,
        help_text='(Data de bipagem)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Data final', required=False,
        help_text='(Se não informar, assume igual a inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))


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
    local = forms.CharField(
        label='End. ou Palete', min_length=1, max_length=8,
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


class EsvaziaPaleteForm(forms.Form):
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


class GradeEstoqueTotaisForm(forms.Form):
    CHOICES = [
        ('g', 'Todas as grades'),
        ('d', 'Apenas grades de disponibilidade'),
        ('t', 'Apenas grades totais'),
    ]
    apresenta = forms.ChoiceField(
        choices=CHOICES, initial='t')

    colecao = forms.ChoiceField(
        label='Coleção da referência',
        required=False, initial=None)

    tabela = forms.ChoiceField(
        label='Modelos da tabela de preços',
        required=False, initial=None)

    referencia = forms.CharField(
        label='Referência',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'string',
                'style': 'text-transform:uppercase;',
                'placeholder': '0...',
            }
        )
    )

    modelo = forms.CharField(
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'number',
                'placeholder': '0',
            }
        )
    )

    CHOICES_PAGINADOR = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    usa_paginador = forms.ChoiceField(
        label='Utiliza paginador',
        choices=CHOICES_PAGINADOR, initial='s')

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(GradeEstoqueTotaisForm, self).__init__(*args, **kwargs)

        cursor = db_cursor_so(self.request)

        CHOICES = [(None, '(Todas)')]
        colecoes = Colecao.objects.all().order_by('colecao')
        for colecao in colecoes:
            CHOICES.append((
                colecao.colecao,
                f"{colecao.colecao}-{colecao.descr_colecao}"
            ))
        self.fields['colecao'].choices = CHOICES

        CHOICES_TABELA = [(None, '--')]
        tabelas = get_tabela_preco(cursor, col=1, mes=1, order='d')
        for tabela in tabelas:
            codigo_tabela = "{:02d}.{:02d}.{:02d}".format(
                tabela['col_tabela_preco'],
                tabela['mes_tabela_preco'],
                tabela['seq_tabela_preco'],
            )
            CHOICES_TABELA.append((
                codigo_tabela,
                f"{codigo_tabela}-{tabela['descricao']}"
            ))
        self.fields['tabela'].choices = CHOICES_TABELA

    def clean_referencia(self):
        cleaned = self.cleaned_data['referencia']
        cleaned = '' if len(cleaned) == 0 else cleaned.upper().zfill(5)
        data = self.data.copy()
        data['referencia'] = cleaned
        self.data = data
        return cleaned


class SolicitacaoForm(forms.Form):
    solicitacao = forms.CharField(
        label='Solicitação',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                'type': 'number',
                'autofocus': 'autofocus',
            },
        ),
    )


class FinalizaEmpenhoOpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        required=True,
        min_length=1,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                'type': 'number',
            }
        )
    )

class SolicitacoesForm(forms.Form):
    solicitacao = forms.CharField(
        label='Solicitação',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                'type': 'number',
                'autofocus': 'autofocus',
            },
        ),
    )
    pedido_destino = forms.CharField(
        label='Pedido destino',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 9,
                'type': 'number',
            },
        ),
    )
    ref_destino = forms.CharField(
        label='Referência destino',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'string',
                'style': 'text-transform:uppercase;',
                'placeholder': '0...',
            }
        )
    )
    ref_reservada = forms.CharField(
        label='Referência reservada',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'string',
                'style': 'text-transform:uppercase;',
                'placeholder': '0...',
            }
        )
    )
    lote = forms.CharField(
        min_length=9,
        max_length=9,
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 9,
                'type': 'number',
            }
        )
    )
    op = forms.CharField(
        label='OP',
        required=False,
        min_length=1,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                'type': 'number',
            }
        )
    )
    CHOICES = [
        (' ', "Não filtra"),
        ('1', "1-A confirmar"),
        ('2', "2-Confirmado"),
        ('3', "3-Programado"),
        ('4', "4-Solicitado"),
        ('5', "5-Baixado"),
        ('9', "9-Cancelado"),
    ]
    com_lotes_situacao_de = forms.ChoiceField(
        label='Com lotes em situação: De',
        choices=CHOICES,
        initial=' ',
    )
    com_lotes_situacao_ate = forms.ChoiceField(
        label='Até',
        choices=CHOICES,
        initial=' ',
    )
    # sem_lotes_situacao_de = forms.ChoiceField(
    #     label='Sem lotes na situação: De',
    #     choices=CHOICES,
    #     initial=' ',
    # )
    # sem_lotes_situacao_ate = forms.ChoiceField(
    #     label='Até',
    #     choices=CHOICES,
    #     initial=' ',
    # )
    page = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    def clean_ref_destino(self):
        cleaned = self.cleaned_data['ref_destino']
        if len(cleaned) == 0:
            return ''
        return cleaned.upper().zfill(5)

    def clean_ref_reservada(self):
        cleaned = self.cleaned_data['ref_reservada']
        if len(cleaned) == 0:
            return ''
        return cleaned.upper().zfill(5)


class QtdEmLoteForm(forms.Form):
    quant = forms.IntegerField(
        label='Qtd. peças',
        min_value=1,
        max_value=100,
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'size': 3,
                'autofocus': 'autofocus',
            }
        )
    )

    lote = forms.CharField(
        max_length=9,
        min_length=9,
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'size': 9,
            }
        )
    )

    quant_conf = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    lote_conf = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )


class ListaLoteInventForm(forms.Form):
    inventario = forms.ModelChoiceField(
        label='Inventário',
        queryset=Inventario.objects.all().order_by('-inicio'),
        initial=Inventario.objects.order_by('-inicio').first(),
    )
    filtro = forms.CharField(
        min_length=1,
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'autofocus': 'autofocus'
            }
        )
    )

    page = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

class ConfrontaQtdLoteForm(forms.Form):
    usuario = forms.ChoiceField(
        label='Usuário',
        required=False,
        initial=None
    )

    def __init__(self, *args, **kwargs):
        super(ConfrontaQtdLoteForm, self).__init__(*args, **kwargs)
        invent_lotes = InventarioLote.objects.filter(
            inventario=Inventario.objects.order_by('-inicio').first(),
        ).distinct('usuario')
        CHOICES_USUARIO = [(None, 'Todos')]
        for invent_lote in invent_lotes:
            CHOICES_USUARIO.append((
                invent_lote.usuario,
                invent_lote.usuario.username,
            ))
        self.fields['usuario'].choices = CHOICES_USUARIO


class NaoEnderecadosForm(forms.Form):
    sol_de = forms.CharField(
        label='Solicitação: De',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'autofocus': 'autofocus',
                'size': 5,
                'type': 'number',
            }
        )
    )

    sol_ate = forms.CharField(
        label='Até',
        required=False,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'autofocus': 'autofocus',
                'size': 5,
                'type': 'number',
            }
        )
    )

    situacao = forms.CharField(
        label='Situações',
        min_length=1,
        max_length=5,
        required=False,
        initial='1234',
        widget=forms.TextInput(
            attrs={
                'size': 5,
            }
        )
    )

    CHOICES_PAGINADOR = [
        ('s', 'Sim'),
        ('n', 'Não'),
    ]
    usa_paginador = forms.ChoiceField(
        label='Utiliza paginador',
        choices=CHOICES_PAGINADOR, initial='s')

    page = forms.IntegerField(
        label='Página',
        min_value=1,
        required=False,
        initial=1,
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'size': 5,
            }
        )
    )


class PaleteSolicitacaoForm(forms.Form):
    solicitacao = forms.CharField(
        label='Solicitação',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                'type': 'number',
                'autofocus': 'autofocus',
            },
        ),
    )


class PaletesForm(forms.Form):
    filtro = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 79,
                'style': 'vertical-align:top;',
            }
        )
    )


class EnderecaGrupoForm(forms.Form):
    endereco = forms.CharField(
        label='Mascara de endereço',
        help_text='(exemplo: 2Y0|401-418)',
        widget=forms.TextInput(),
    )
    paletes = forms.CharField(
        help_text='(ou lotes)',
        widget=forms.Textarea(
            attrs={
                'rows': 20,
                'cols': 20,
                'style': 'vertical-align:top;',
            }
        )
    )


class RealocaSolicitacoesForm(forms.Form):
    a = FormWidgetAttrs()

    endereco = forms.CharField(
        label='Endereço',
        required=False,
        min_length=1,
        widget=forms.TextInput(
            attrs={
                'size': 20,
                **a.string_upper,
                **a.autofocus,
            }
        )
    )

    solicitacoes = forms.CharField(
        label='Solicitações',
        required=False,
        widget=forms.TextInput(
            attrs={
                'size': 40,
                'type': 'text',
            }
        )
    )

    modelo = forms.CharField(
        required=True,
        min_length=1,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'size': 5,
                'type': 'number',
            }
        )
    )

    cor = forms.CharField(
        required=True,
        min_length=1,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'size': 6,
                **a.string_upper,
                **a.placeholder_0,
            }
        )
    )

    tam = forms.CharField(
        label='Tamanho',
        required=True,
        min_length=1,
        max_length=3,
        widget=forms.TextInput(
            attrs={
                'size': 3,
                **a.string_upper,
            }
        )
    )

    CHOICES = [
        ('ce', "Com empenho"),
        ('pe', "Parcialmente empenhado"),
    ]
    qtd_empenhada = forms.ChoiceField(
        label='Quantidade empenhada',
        choices=CHOICES,
        initial='s',
    )

    CHOICES = [
        ('n', "Não"),
        ('s', "Sim"),
    ]
    forca_oti = forms.ChoiceField(
        label='Força otimização após comparativo',
        choices=CHOICES,
        initial='n',
    )

    def clean_cor(self):
        cleaned = self.cleaned_data['cor']
        if len(cleaned) == 0:
            cleaned = ''
        else:
            cleaned = cleaned.upper().zfill(6)

        data = self.data.copy()
        data['cor'] = cleaned
        self.data = data
        return cleaned

    def clean_tam(self):
        cleaned = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = cleaned
        self.data = data
        return cleaned

    def clean_endereco(self):
        cleaned = self.cleaned_data.get('endereco', '').strip().upper()
        data = self.data.copy()
        data['endereco'] = cleaned
        self.data = data
        return cleaned

from pprint import pprint

from django import forms

from fo2.connections import db_cursor_so

from cd.queries.novo_modulo.solicitacao import get_solicitacao


class EtiquetasParciaisForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
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
        cursor = db_cursor_so(self.request)

        numero = self.cleaned_data.get('numero', '')

        solicitacao = get_solicitacao(
            cursor,
            solicitacao=numero,
        )
        if len(solicitacao) == 0:
            raise forms.ValidationError("Solicitação não existe")

        # solicitacao_prt = lotes.models.SolicitaLotePrinted.objects.filter(
        #     solicitacao=solicitacao
        # )
        # if len(solicitacao_prt) != 0:
        #     if not solicitacao.can_print:
        #         raise forms.ValidationError("Etiquetas já foram impressas")

        if all(map(
            lambda r: r['qtd_ori'] == r['qtde'],
            solicitacao,
        )):
            raise forms.ValidationError("Sem lotes parciais")

        return numero

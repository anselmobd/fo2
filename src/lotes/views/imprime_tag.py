import os
from pathlib import Path
from pprint import pprint

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.classes import TermalPrint

import lotes.models as models
from lotes.forms import ImprimeTagForm


class ImprimeTag(LoginRequiredMixin, View):
    login_url = '/intradm/login/'
    Form_class = ImprimeTagForm
    template_name = 'lotes/imprime_tag.html'
    title_name = 'Imprime TAG'

    def mount_context_and_print(self, cursor, item, quant):
        context = {
            'item': item,
            'quant': quant,
        }

        do_print = True
        try:
            impresso = models.Impresso.objects.get(
                nome='TAG 5 vertical')
        except models.Impresso.DoesNotExist:
            impresso = None
        if impresso is None:
            context.update({
                'msg_erro': 'Impresso não cadastrado',
            })
            do_print = False

        if do_print:
            try:
                usuario_impresso = models.UsuarioImpresso.objects.get(
                    usuario=self.request.user, impresso=impresso)
            except models.UsuarioImpresso.DoesNotExist:
                usuario_impresso = None
            if usuario_impresso is None:
                context.update({
                    'msg_erro': 'Impresso não cadastrado para o usuário',
                })
                do_print = False

        if do_print:
            data = [{'item': item,
                     'quant': quant}, ]
            teg = TermalPrint(usuario_impresso.impressora_termica.nome)
            teg.template(
                usuario_impresso.modelo.gabarito,
                '\r\n', strip_end_line='\r\n')
            teg.printer_start()
            try:
                icoluna = 0
                bloco = {'tags': []}
                for row in data:
                    ref = row['item'].produto.imp_cod
                    if ref is None:
                        ref = row['item'].produto.referencia
                    ref = ref.strip()

                    tam = row['item'].tamanho.imp_cod
                    if tam is None:
                        tam = row['item'].tamanho.tamanho.nome
                    tam = tam.strip()

                    cor = ''
                    if row['item'].produto.cor_no_tag:
                        cor = row['item'].cor.imp_cod
                        if cor is None:
                            cor = row['item'].cor.cor
                        cor = cor.strip()

                    gtin = row['item'].gtin_tag
                    if gtin is None:
                        gtin = row['item'].gtin
                    gtin = gtin.strip()

                    nome_arquivo = (os.path.join(
                        settings.MEDIA_ROOT,
                        row['item'].produto.imagem_tag.imagem.name))
                    imagem = Path(nome_arquivo).read_bytes()
                    bloco['imagem'] = imagem

                    comp = row['item'].cor.composicao
                    if not comp:
                        comp = row['item'].produto.composicao
                    comp = comp.composicaolinha_set.all().values()
                    lin_count = len(comp)
                    comp_dict = {linha['ordem']: linha['linha']
                                 for linha in comp}
                    linha = {n: '' for n in range(1, 8)}
                    lin_inicial = 7 - lin_count
                    for n in range(1, lin_count+1):
                        linha[lin_inicial + n] = comp_dict[n].strip()

                    while row['quant'] > 0:
                        tag = {
                            'ref': ref,
                            'tam': tam,
                            'cor': cor,
                            'gtin': gtin,
                            'lin_count': lin_count,
                            'linha1': linha[1],
                            'linha2': linha[2],
                            'linha3': linha[3],
                            'linha4': linha[4],
                            'linha5': linha[5],
                            'linha6': linha[6],
                            'linha7': linha[7],
                        }
                        bloco['tags'].append(tag)
                        row['quant'] -= 1
                        icoluna += 1

                        if icoluna == 5:
                            teg.context(bloco)
                            teg.printer_send()
                            icoluna = 0
                            bloco['tags'] = []

                if icoluna != 0:
                    teg.context(bloco)
                    teg.printer_send()
            finally:
                teg.printer_end()

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            item = form.cleaned_data['item']
            quant = form.cleaned_data['quant']

            cursor = db_cursor_so(request)
            context.update(self.mount_context_and_print(cursor, item, quant))
        context['form'] = form
        return render(request, self.template_name, context)

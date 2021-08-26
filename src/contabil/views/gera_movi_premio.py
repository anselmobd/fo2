import re
from pprint import pprint

from django.shortcuts import render
from django.views import View

import contabil.forms


class GeraMoviPremio(View):

    def __init__(self, *args, **kwargs):
        super(GeraMoviPremio, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.UploadArquivoForm
        self.template_name = 'contabil/gera_movi_premio.html'
        self.title_name = 'Gera movimento prêmio'

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST, request.FILES)
        if form.is_valid():
            lines = []
            for line in request.FILES['arquivo']:
                line = line.decode('utf-8', errors='ignore').strip("\n").strip()
                lines.append(line)
            # context['original'] = "orig"  # "\n".join(lines)

            if not lines:
                context['erro'] = "Arquivo vazio"
            else:
                registros = []
                for line in lines:
                    colunas = line.split(";")
                    funcionario = colunas[0]
                    valor = colunas[-1]
                    dados_func = re.split('-| |"', funcionario)
                    if len(dados_func) > 1:
                        if dados_func[1].isdigit():
                            pprint(dados_func)
                            ident = f"{int(dados_func[1]):05}"
                            registros.append(';'.join([
                                ident,
                                "9R44FO",
                                valor,
                                "",
                                "",
                                "",
                            ]))
                            registros.append(';'.join([
                                ident,
                                "9R45FO",
                                valor,
                                "",
                                "",
                                "",
                            ]))

                context['systextil'] = "\n".join(registros)
                context['systextil_download'] = "%0A%0D".join(registros)
                context['systextil_file'] = f"Nasajon_{request.FILES['arquivo']._name}"
            
        else:
            context['erro'] = 'Erro inexperado!'
        context['form'] = form
        return render(request, self.template_name, context)

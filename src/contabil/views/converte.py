from pprint import pprint

from django.shortcuts import render
from django.views import View

import contabil.forms


class Converte(View):

    def __init__(self, *args, **kwargs):
        super(Converte, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.UploadArquivoForm
        self.template_name = 'contabil/converte.html'
        self.title_name = 'Converte para importação'

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
            i_contas = -1
            for i, line in enumerate(request.FILES['arquivo']):
                line = line.decode('utf-8', errors='ignore').strip("\n").strip()
                lines.append(line)
                if line == '[Contas]':
                    i_contas = i
            context['original'] = "\n".join(lines)

            if i_contas == -1:
                context['erro'] = "Arquivo sem '[Contas]'"
            else:

                codigos = {}
                for idx in range(i_contas, len(lines)):
                    linha = lines[idx]
                    if "=" not in linha:
                        continue
                    codigo, linha = tuple(linha.split("="))
                    colunas = linha.split(",")
                    codigos[codigo] = colunas[2].strip('"')

                registros = []
                for idx in range(i_contas):
                    linha = lines[idx]
                    if len(linha) == 0:
                        continue
                    colunas = linha[1:-1].split('","')
                    conta_d = colunas[1]
                    conta_c = colunas[2]
                    data = colunas[3]
                    if data == "D":
                        continue

                    valor = float(colunas[4].replace(",", "."))
                    descricao = "/".join([
                        codigos[conta_d],
                        codigos[conta_c],
                    ])

                    registros.append(" ".join([
                        "002",
                        data,
                        f"{int(conta_d):020}",
                        "0000",
                        "D",
                        "700001",
                        "0502",
                        f"{descricao:100}",
                        f"{valor:015.2f}"
                    ]))

                    registros.append(" ".join([
                        "002",
                        data,
                        f"{int(conta_c):020}",
                        "0000",
                        "C",
                        "700001",
                        "0502",
                        f"{descricao:100}",
                        f"{valor:015.2f}"
                    ]))

            context['systextil'] = "\n".join(registros)
            context['systextil_download'] = "%0A%0D".join(registros)
            context['systextil_file'] = f"Systextil_{request.FILES['arquivo']._name}"
            
        else:
            context['erro'] = 'Erro inexperado!'
        context['form'] = form
        return render(request, self.template_name, context)

from pprint import pprint

from django.shortcuts import render


def view(request):
    template_name = 'contabil/nasajon.html'
    context = {
        'titulo': "Nasajon",
        'agenda': [
            {
                'titulo': "10/10/2022 - Kickoff",
                'subdir': "2022-10-10 kickoff",
                'docs': {
                    'MAIS001 - Kickoff ERP - Tussor - GP Sérgio Santos':
                        "MAIS001 - KICKOFF ERP - TUSSOR CONFECCOES LTDA - GP SERGIO SANTOS.pdf",
                    'MAIS002 - Tussor - Termo de Abertura do Projeto (TAP)':
                        "MAIS002 - TUSSOR CONFECCOES LTDA- Termo de Abertura do Projeto (TAP).docx.pdf",
                    'Ordem de Servico - 4181':
                        "Ordem de Servico - 4181.pdf",
                    'Cronograma Versão 1':
                        "TUSSOR CONFECCOES LTDA - Cronograma V1.pdf",
                },
            },
            {
                'titulo': "19/10/2022 - Levantamento fiscal",
                'subdir': "2022-10-19 levantamento fiscal",
                'docs': {
                    'MAIS013 - Levantamento de Processos':
                        "MAIS013 - Levantamento de Processos TUSSOR CONFECÇÕES.docx.pdf",
                    'Ordem de Servico - 4301':
                        "Ordem de Servico - 4301.pdf",
                },
            },
            {
                'titulo': "20/10/2022 - Levantamento contábil",
                'subdir': "2022-10-20 levantamento contábil",
                'docs': {
                    'MAIS013 - Levantamento de Processos do Contábil':
                        "MAIS013 - Levantamento de Processos do Contábil.pdf",
                    'Ordem de Servico - 4324':
                        "Ordem de Servico - 4324.pdf",
                },
                'files': {
                    '14h31': "kkq-rieh-qxp (2022-10-20 14 31 GMT-3).mp4",
                },
            },
            {
                'titulo': "24/10/2022 - Preparação de aderência",
                'subdir': "2022-10-24 preparação aderência",
                'docs': {
                    'Ordem de Servico - 4359':
                        "Ordem de Servico - 4359.pdf",
                },
            },
            {
                'titulo': "25/10/2022 - Apresentação aderência",
                'subdir': "2022-10-25 apresentação aderência",
                'docs': {
                    'Ordem de Servico - 4381':
                        "Ordem de Servico - 4381.pdf",
                },
                'files': {
                    '14h31': "kkq-rieh-qxp (2022-10-25 14 31 GMT-3).mp4",
                },
            },
            {
                'titulo': "26/10/2022 - Definição de processos e Scritta 1 de 3",
                'subdir': "2022-10-26 def. processos e scritta 1 de 3",
                'docs': {
                    'MAIS014 - Definição de Processos Contábil':
                        "MAIS014 - Definição de Processos Contábil.docx.pdf",
                    'Ordem de Servico - 4393':
                        "Ordem de Servico - 4393.pdf",
                },
            },
            {
                'titulo': "27/10/2022 - Scritta 2 de 3",
                'subdir': "2022-10-27 scritta 2 de 3",
                'docs': {
                    'Ordem de Servico - 4411':
                        "Ordem de Servico - 4411.pdf",
                },
                'files': {
                    '14h21': "kkq-rieh-qxp (2022-10-27 14 21 GMT-3).mp4",
                },
            },
            {
                'titulo': "01/11/2022 - Scritta 3 de 3",
                'subdir': "2022-11-01 scritta 3 de 3",
                'docs': {
                    'Ordem de Servico - 4464':
                        "Ordem de Servico - 4464.pdf",
                },
                'files': {
                    '14h14': "kkq-rieh-qxp (2022-11-01 14 14 GMT-3).mp4",
                    '15h48': "kkq-rieh-qxp (2022-11-01 15 48 GMT-3).mp4",
                }
            },
            {
                'titulo': "07/11/2022 - Contábil 1 de 3",
                'subdir': "2022-11-07 contabil 1 de 3",
                'docs': {
                    'Ordem de Servico - 4508':
                        "Ordem de Servico - 4508.pdf",
                },
                'files': {
                    '15h48': "kkq-rieh-qxp (2022-11-07 14 32 GMT-3).mp4",
                },
            },
            {
                'titulo': "10/11/2022 - Contábil 2 de 3",
                'subdir': "2022-11-10 contábil 2 de 3",
                'docs': {
                    'Ordem de Servico - 4550':
                        "Ordem de Servico - 4550.pdf",
                },
                'files': {
                    '14h32': "kkq-rieh-qxp (2022-11-10 14 21 GMT-3).mp4",
                },
            },
            {
                'titulo': "16/11/2022 - Contábil 3 de 3",
                'subdir': "2022-11-16 contábil 3 de 3",
                'docs': {
                    'Ordem de Servico - 4583':
                        "Ordem de Servico - 4583.pdf",
                },
                'files': {
                    '14h17': "kkq-rieh-qxp (2022-11-16 14 17 estimado GMT-3).mp4",
                    '15h57': "kkq-rieh-qxp (2022-11-16 15 57 GMT-3).mp4",
                },
            },
            {
                'titulo': "21/11/2022 - Simulação Scritta",
                'subdir': "2022-11-21 simulação scritta",
                'docs': {
                    'Ordem de Servico - 4636':
                        "Ordem de Servico - 4636.pdf",
                },
                'files': {
                    '14h24': "kkq-rieh-qxp (2022-11-21 14 24 GMT-3).mp4",
                    '16h15': "kkq-rieh-qxp (2022-11-21 16 15 GMT-3).mp4",
                    '16h58': "kkq-rieh-qxp (2022-11-21 16 58 GMT-3).mp4",
                },
            },
            {
                'titulo': "22/11/2022 - Simulação Contábil",
                'subdir': "2022-11-22 simulação contábil",
                'docs': {
                    'Ordem de Servico - 4663':
                        "Ordem de Servico - 4663.pdf",
                },
                'files': {
                    '14h08': "kkq-rieh-qxp (2022-11-22 14 08 GMT-3).mp4",
                },
            },
            {
                'titulo': "23/11/2022 - Setup Scritta",
                'subdir': "2022-11-23 Setup Scritta",
                'docs': {
                    'Ordem de Servico - 4680':
                        "Ordem de Servico - 4680.pdf",
                },
                'files': {
                    '14h20': "kkq-rieh-qxp (2022-11-23 14 20 GMT-3).mp4",
                },
            },
            {
                'titulo': "24/11/2022 - Setup Contábil",
                'subdir': "2022-11-24 Setup Contábil",
                'docs': {
                    'Ordem de Servico - 4687':
                        "Ordem de Servico - 4687.pdf",
                },
                'files': {
                    '09h23': "kkq-rieh-qxp (2022-11-24 09 23 GMT-3).mp4",
                },
            },
            {
                'titulo': "29/11/2022 - Acompanhamento produção 1 de 4",
                'subdir': "2022-11-29 Acompanhamento produção 1 de 4",
                'docs': {
                    'Ordem de Servico - 4720':
                        "Ordem de Servico - 4720.pdf",
                },
                'files': {
                    '14h22': "kkq-rieh-qxp (2022-11-29 14 22 GMT-3).mp4",
                },
            },
            {
                'titulo': "30/11/2022 - Acompanhamento produção 2 de 4",
                'subdir': "2022-11-30 Acompanhamento produção 2 de 4",
                'docs': {
                    'Ordem de Servico - 4733':
                        "Ordem de Servico - 4733.pdf",
                },
                'files': {
                    '14h10': "kkq-rieh-qxp (2022-11-30 14 10 GMT-3).mp4",
                    '16h10': "kkq-rieh-qxp (2022-11-30 16 10 GMT-3).mp4",
                },
            },
            {
                'titulo': "01/12/2022 - Acompanhamento produção 3 de 4",
                'subdir': "2022-12-01 Acompanhamento produção 3 de 4",
                'docs': {
                    'Ordem de Servico - 4748':
                        "Ordem de Servico - 4748.pdf",
                },
                'files': {
                    '14h20': "kkq-rieh-qxp (2022-12-01 14 20 GMT-3).mp4",
                    '16h01': "kkq-rieh-qxp (2022-12-01 16 01 GMT-3).mp4",
                },
            },
        ]
    }
    return render(request, template_name, context)

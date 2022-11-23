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
                }
            },
            {
                'titulo': "19/10/2022 - Levantamento fiscal",
            },
            {
                'titulo': "20/10/2022 - Levantamento contábil",
                'files': {
                    '14h31': "kkq-rieh-qxp (2022-10-20 14 31 GMT-3).mp4",
                },
            },
            {
                'titulo': "24/10/2022 - Preparação de aderência",
            },
            {
                'titulo': "25/10/2022 - Apresentação aderência",
                'files': {
                    '14h31': "kkq-rieh-qxp (2022-10-25 14 31 GMT-3).mp4",
                },
            },
            {
                'titulo': "26/10/2022 - Definição de processos e Scritta 1 de 3",
            },
            {
                'titulo': "27/10/2022 - Scritta 2 de 3",
                'files': {
                    '14h21': "kkq-rieh-qxp (2022-10-27 14 21 GMT-3).mp4",
                },
            },
            {
                'titulo': "01/11/2022 - Scritta 3 de 3",
                'files': {
                    '14h14': "kkq-rieh-qxp (2022-11-01 14 14 GMT-3).mp4",
                    '15h48': "kkq-rieh-qxp (2022-11-01 15 48 GMT-3).mp4",
                }
            },
            {
                'titulo': "07/11/2022 - Contabil 1 de 3",
                'files': {
                    '15h48': "kkq-rieh-qxp (2022-11-07 14 32 GMT-3).mp4",
                },
            },
            {
                'titulo': "10/11/2022 - Contábil 2 de 3",
                'files': {
                    '14h32': "kkq-rieh-qxp (2022-11-10 14 21 GMT-3).mp4",
                },
            },
            {
                'titulo': "16/11/2022 - Contábil 3 de 3",
            },
            {
                'titulo': "21/11/2022 - Simulação scritta",
                'files': {
                    '14h24': "kkq-rieh-qxp (2022-11-21 14 24 GMT-3).mp4",
                    '16h15': "kkq-rieh-qxp (2022-11-21 16 15 GMT-3).mp4",
                    '16h58': "kkq-rieh-qxp (2022-11-21 16 58 GMT-3).mp4",
                },
            },
            {
                'titulo': "22/11/2022 - Simulação contábil",
            },
        ]
    }
    return render(request, template_name, context)

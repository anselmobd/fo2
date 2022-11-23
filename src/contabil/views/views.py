from django.shortcuts import render

from geral.functions import get_empresa


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'contabil/index_agator.html')
    else:
        return render(request, 'contabil/index.html')


def nasajon(request):
    template_name = 'contabil/nasajon.html'
    context = {
        'titulo': "Nasajon",
        'videos': [
            {'file': "kkq-rieh-qxp (2022-10-20 14 31 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-10-25 14 31 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-10-27 14 21 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-01 14 14 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-01 15 48 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-07 14 32 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-10 14 21 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-21 14 24 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-21 16 15 GMT-3).mp4"},
            {'file': "kkq-rieh-qxp (2022-11-21 16 58 GMT-3).mp4"},
        ]
    }
    return render(request, template_name, context)

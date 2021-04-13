from pprint import pprint

from django.shortcuts import render

from base.views import O2BaseGetPostView

import servico.forms


def index(request):
    return render(request, 'servico/index.html')


class Ordens(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Ordens, self).__init__(*args, **kwargs)
        self.Form_class = servico.forms.OrdensForm
        self.template_name = 'servico/ordens.html'
        self.title_name = 'Ordens'


from pprint import pprint

from django.shortcuts import render

from base.views import O2BaseGetView


class Demorada(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Demorada, self).__init__(*args, **kwargs)
        self.template_name = 'systextil/dba/demorada.html'
        self.title_name = 'Queries Demoradas'

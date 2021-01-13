from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View

import beneficia.forms



class Ob(View):

    def __init__(self):
        self.Form_class = beneficia.forms.ObForm
        self.template_name = 'beneficia/ob.html'
        self.title_name = 'OB'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()
        context = {}

        ob = form.cleaned_data['ob']

        context.update({
            'ob': ob,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)

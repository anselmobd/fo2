from pprint import pprint

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.shortcuts import render

from base.views import O2BaseGetView


class Demorada(LoginRequiredMixin, PermissionRequiredMixin, O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Demorada, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/demorada.html'
        self.title_name = 'Queries Demoradas'

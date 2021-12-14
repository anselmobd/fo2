from django.urls import re_path

from systextil.views.dba import (
    demorada,
    info_sessao,
    travadora,
)


urlpatterns = [

    re_path(r'^demorada/$', demorada.Demorada.as_view(), name='demorada'),

    re_path(r'^info_sessao/$', info_sessao.InfoSessao.as_view(), name='info_sessao'),

    re_path(r'^travadora/$', travadora.Travadora.as_view(), name='travadora'),

]

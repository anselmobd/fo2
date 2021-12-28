from django.urls import re_path

from systextil.views.dba import (
    demorada,
    info_sessao,
    travadora,
    kill_sessao,
)


urlpatterns = [

    re_path(r'^demorada/$', demorada.Demorada.as_view(), name='demorada'),
    re_path(r'^demorada/(?P<segundos>\d+)/$',
        demorada.Demorada.as_view(), name='demorada__get'),

    re_path(r'^info_sessao/$', info_sessao.InfoSessao.as_view(), name='info_sessao'),
    re_path(r'^info_sessao/(?P<sessao_id>\d+)/$',
        info_sessao.InfoSessao.as_view(), name='info_sessao__get'),

    re_path(r'^kill_sessao/(?P<id_serial>.+)/$',
        kill_sessao.KillSessao, name='kill_sessao__get'),

    re_path(r'^travadora/$', travadora.Travadora.as_view(), name='travadora'),

]

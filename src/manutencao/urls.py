from django.urls import re_path

from . import views


app_name = 'manutencao'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^maquinas/$',
        views.Maquinas.as_view(), name='maquinas'),

    re_path(r'^rotinas/$',
        views.Rotinas.as_view(), name='rotinas'),

    re_path(r'^rotina/(?P<id>\d+)/$',
        views.Rotina.as_view(), name='rotina__get'),

    re_path(r'^executar/$',
        views.Executar.as_view(), name='executar'),

    re_path(r'^imprimir/(?P<rotina>\d+)/(?P<maquina>\d+)/(?P<data>.+)/$',
        views.Imprimir.as_view(), name='imprimir'),

    re_path(r'^cria_os/(?P<rotina>\d+)/(?P<maquina>\d+)/(?P<data>.+)/$',
        views.CriaOS.as_view(), name='cria_os'),
]

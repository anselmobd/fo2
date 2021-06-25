from django.conf.urls import url

from . import views


app_name = 'manutencao'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^maquinas/$',
        views.Maquinas.as_view(), name='maquinas'),

    url(r'^rotinas/$',
        views.Rotinas.as_view(), name='rotinas'),

    url(r'^rotina/(?P<id>\d+)/$',
        views.Rotina.as_view(), name='rotina__get'),

    url(r'^executar/$',
        views.Executar.as_view(), name='executar'),

    url(r'^imprimir/(?P<rotina>\d+)/(?P<maquina>\d+)/(?P<data>.+)/$',
        views.Imprimir.as_view(), name='imprimir'),

    url(r'^cria_os/(?P<rotina>\d+)/(?P<maquina>\d+)/(?P<data>.+)/$',
        views.CriaOS.as_view(), name='cria_os'),
]

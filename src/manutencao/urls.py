from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^rotinas/$',
        views.Rotinas.as_view(), name='rotinas'),

    url(r'^imprimir/(?P<roteiro>\d+)/(?P<maquina>\d+)/(?P<data>\d+)/$',
        views.Imprimir.as_view(), name='imprimir'),
]

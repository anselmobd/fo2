from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^posicao/$', views.posicao, name='posicao'),
    url(r'^posicao/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='detalhes_lote'),
]

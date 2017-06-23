from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^posicao/$', views.posicao, name='posicao'),
    url(r'^posicao.old/$', views.posicaoOri, name='posicaoOri'),
    url(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='detalhes_lote'),
    url(r'^respons/$', views.respons, name='respons'),
    url(r'^op/$', views.op, name='op'),
]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='cd'),
    url(r'^lote_local/$', views.LotelLocal.as_view(), name='cd_lote_local'),
    url(r'^conferencia/$', views.Conferencia.as_view(), name='cd_conferencia'),
    url(r'^estoque/$', views.Estoque.as_view(), name='cd_estoque'),
    url(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='cd_estoque_filtro'),
    url(r'^troca_local/$', views.TrocaLocal.as_view(), name='cd_troca_local'),
    url(r'^inconsist/$', views.Inconsistencias.as_view(), name='cd_inconsist'),
    url(r'^inconsist/(?P<ordem>.-?)/(?P<opini>\d+)/$',
        views.Inconsistencias.as_view(), name='cd_inconsist_opini'),
    url(r'^inconsist_detalhe/(?P<op>\d+)/$',
        views.InconsistenciasDetalhe.as_view(),
        name='cd_inconsist_detalhe_op'),
    url(r'^mapa/$', views.Mapa.as_view(), name='cd_mapa'),
]

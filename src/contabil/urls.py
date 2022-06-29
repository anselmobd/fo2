from django.urls import re_path

from . import views


app_name = 'contabil'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^busca_nf/$', views.busca_nf.BuscaNF.as_view(),
        name='busca_nf'),

    re_path(r'^converte/$', views.Converte.as_view(), name='converte'),

    re_path(r'^infadprod/(?P<pedido>.+)?/?$',
        views.InfAdProd.as_view(), name='infadprod'),

    re_path(r'^nota_fiscal/$', views.NotaFiscal.as_view(), name='nota_fiscal'),
    re_path(r'^nota_fiscal/(?P<empresa>\d+)/(?P<nf>\d+)/$', views.NotaFiscal.as_view(),
        name='nota_fiscal__get2'),

    re_path(r'^remeindu/$', views.RemessaIndustr.as_view(), name='remeindu'),

    re_path(r'^remeindunf/?$',
        views.RemessaIndustrNF.as_view(), name='remeindunf'),
    re_path(r'^remeindunf/(?P<nf>.+)?/(?P<detalhe>.+)?/$',
        views.RemessaIndustrNF.as_view(), name='remeindunf__get'),

]

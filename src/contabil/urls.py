from django.urls import re_path, path

from . import views
from contabil.views import (
    nasajon,
    nf_rec_busca,
    nf_recebida,
)


app_name = 'contabil'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^busca_nf/$', views.busca_nf.BuscaNF.as_view(),
        name='busca_nf'),

    re_path(r'^converte/$', views.Converte.as_view(), name='converte'),

    re_path(r'^nasajon/$', nasajon.view, name='nasajon'),

    path(
        'nf_rec_busca/',
        nf_rec_busca.BuscaNFRecebida.as_view(),
        name='nf_rec_busca',
    ),

    path(
        'nf_recebida/',
        nf_recebida.NFRecebida.as_view(),
        name='nf_recebida',
    ),
    path(
        'nf_recebida/<int:empresa>/<int:nf>/<int:nf_ser>/<str:cnpj>/',
        nf_recebida.NFRecebida.as_view(),
        name='nf_recebida__get',
    ),

    re_path(r'^infadprod/(?P<pedido>.+)?/?$',
        views.InfAdProd.as_view(), name='infadprod'),

    path(
        'nota_fiscal/',
        views.NotaFiscal.as_view(),
        name='nota_fiscal',
    ),
    path(
        'nota_fiscal/<int:empresa>/<int:nf>/',
        views.NotaFiscal.as_view(),
        name='nota_fiscal__get',
    ),

    re_path(r'^remeindu/$', views.RemessaIndustr.as_view(), name='remeindu'),

    re_path(r'^remeindunf/?$',
        views.RemessaIndustrNF.as_view(), name='remeindunf'),
    re_path(r'^remeindunf/(?P<nf>.+)?/(?P<detalhe>.+)?/$',
        views.RemessaIndustrNF.as_view(), name='remeindunf__get'),

]

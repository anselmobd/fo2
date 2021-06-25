from django.conf.urls import url

from . import views


app_name = 'contabil'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^infadprod/(?P<pedido>.+)?/?$',
        views.InfAdProd.as_view(), name='infadprod'),

    url(r'^nota_fiscal/$', views.NotaFiscal.as_view(), name='nota_fiscal'),
    url(r'^nota_fiscal/(?P<nf>\d+)/$', views.NotaFiscal.as_view(),
        name='nota_fiscal__get'),

    url(r'^remeindu/$', views.RemessaIndustr.as_view(), name='remeindu'),

    url(r'^remeindunf/?$',
        views.RemessaIndustrNF.as_view(), name='remeindunf'),
    url(r'^remeindunf/(?P<nf>.+)?/(?P<detalhe>.+)?/$',
        views.RemessaIndustrNF.as_view(), name='remeindunf__get'),
]

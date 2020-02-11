from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ficha_cliente/$', views.FichaCliente.as_view(),
        name='ficha_cliente'),
    url(r'^ficha_cliente/(?P<cnpj>.+)/$', views.FichaCliente.as_view(),
        name='ficha_cliente__get'),

    url(r'^vendas_cor/$', views.VendasPorCor.as_view(),
        name='vendas_cor'),

    url(r'^vendas_tamanho/$', views.VendasPorTamanho.as_view(),
        name='vendas_tamanho'),

    url(r'^analise_vendas/$',
        views.estoque.AnaliseVendas.as_view(),
        name='analise_vendas'),

    url(r'^analise_modelo/$',
        views.estoque.AnaliseModelo.as_view(),
        name='analise_modelo'),
    url(r'^analise_modelo/(?P<modelo>.+)/$',
        views.estoque.AnaliseModelo.as_view(),
        name='analise_modelo__get'),

    url(r'^ponderacao/$',
        views.estoque.Ponderacao.as_view(),
        name='ponderacao'),

    url(r'^metas/$',
        views.estoque.Metas.as_view(),
        name='metas'),

    url(r'^verifica_venda/$',
        views.estoque.VerificaVenda.as_view(),
        name='verifica_venda'),

    url(r'^painel_meta_faturamento/$',
        views.PainelMetaFaturamento.as_view(),
        name='painel_meta_faturamento'),

    url(r'^meta_no_ano/$',
        views.MetaNoAno.as_view(),
        name='meta_no_ano'),

]

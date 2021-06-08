from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ficha_cliente/$', views.FichaCliente.as_view(),
        name='ficha_cliente'),
    url(r'^ficha_cliente/(?P<cnpj>.+)/$', views.FichaCliente.as_view(),
        name='ficha_cliente__get'),

    url(r'^vendas/$', views.Vendas.as_view(),
        name='vendas'),

    url(r'^vendas_cor/$', views.VendasPorCor.as_view(),
        name='vendas_cor'),
    url(r'^vendas_cor/(?P<ref>.+)/$',
        views.VendasPorCor.as_view(),
        name='vendas_cor__get'),

    url(r'^vendas_tamanho/$', views.VendasPorTamanho.as_view(),
        name='vendas_tamanho'),
    url(r'^vendas_tamanho/(?P<ref>.+)/$',
        views.VendasPorTamanho.as_view(),
        name='vendas_tamanho__get'),

    url(r'^vendas_por_modelo/$',
        views.VendasPorModelo.as_view(),
        name='vendas_por_modelo'),

    url(r'^analise_modelo_old/$',
        views.AnaliseModeloOld.as_view(),
        name='analise_modelo_old'),
    url(r'^analise_modelo_old/(?P<modelo>.+)/$',
        views.AnaliseModeloOld.as_view(),
        name='analise_modelo_old__get'),

    url(r'^define_meta/$',
        views.DefineMeta.as_view(),
        name='define_meta'),
    url(r'^define_meta/(?P<modelo>.+)/$',
        views.DefineMeta.as_view(),
        name='define_meta__get'),

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

    url(r'^faturamento_para_meta/$',
        views.FaturamentoParaMeta.as_view(),
        name='faturamento_para_meta'),

    url(r'^devolucao_para_meta/$',
        views.DevolucaoParaMeta.as_view(),
        name='devolucao_para_meta'),

    url(r'^pedidos_para_meta/$',
        views.PedidosParaMeta.as_view(),
        name='pedidos_para_meta'),

    url(r'^tabela_de_preco/$',
        views.TabelaDePreco.as_view(),
        name='tabela_de_preco'),
    url(r'^tabela_de_preco/(?P<tabela>.+)/$',
        views.TabelaDePreco.as_view(),
        name='tabela_de_preco__get'),

]

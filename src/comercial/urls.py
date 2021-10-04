from django.urls import re_path

from . import views


app_name = 'comercial'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^ficha_cliente/$', views.FichaCliente.as_view(),
        name='ficha_cliente'),
    re_path(r'^ficha_cliente/(?P<cnpj>.+)/$', views.FichaCliente.as_view(),
        name='ficha_cliente__get'),

    re_path(r'^vendas/$', views.Vendas.as_view(),
        name='vendas'),

    re_path(r'^vendas_cor/$', views.VendasPorCor.as_view(),
        name='vendas_cor'),
    re_path(r'^vendas_cor/(?P<ref>.+)/$',
        views.VendasPorCor.as_view(),
        name='vendas_cor__get'),

    re_path(r'^vendas_tamanho/$', views.VendasPorTamanho.as_view(),
        name='vendas_tamanho'),
    re_path(r'^vendas_tamanho/(?P<ref>.+)/$',
        views.VendasPorTamanho.as_view(),
        name='vendas_tamanho__get'),

    re_path(r'^vendas_por_modelo/$',
        views.VendasPorModelo.as_view(),
        name='vendas_por_modelo'),

    re_path(r'^analise_modelo_old/$',
        views.AnaliseModeloOld.as_view(),
        name='analise_modelo_old'),
    re_path(r'^analise_modelo_old/(?P<modelo>.+)/$',
        views.AnaliseModeloOld.as_view(),
        name='analise_modelo_old__get'),

    re_path(r'^define_meta/$',
        views.DefineMeta.as_view(),
        name='define_meta'),
    re_path(r'^define_meta/(?P<modelo>.+)/$',
        views.DefineMeta.as_view(),
        name='define_meta__get'),

    re_path(r'^ponderacao/$',
        views.estoque.Ponderacao.as_view(),
        name='ponderacao'),

    re_path(r'^metas/$',
        views.estoque.Metas.as_view(),
        name='metas'),

    re_path(r'^verifica_venda/$',
        views.estoque.VerificaVenda.as_view(),
        name='verifica_venda'),

    re_path(r'^painel_meta_faturamento/$',
        views.PainelMetaFaturamento.as_view(),
        name='painel_meta_faturamento'),

    re_path(r'^meta_no_ano/$',
        views.MetaNoAno.as_view(),
        name='meta_no_ano'),

    re_path(r'^faturamento_para_meta/$',
        views.FaturamentoParaMeta.as_view(),
        name='faturamento_para_meta'),

    re_path(r'^devolucao_para_meta/$',
        views.DevolucaoParaMeta.as_view(),
        name='devolucao_para_meta'),

    re_path(r'^pedidos_para_meta/$',
        views.PedidosParaMeta.as_view(),
        name='pedidos_para_meta'),

    re_path(r'^tabela_de_preco/$',
        views.TabelaDePreco.as_view(),
        name='tabela_de_preco'),
    re_path(r'^tabela_de_preco/(?P<tabela>.+)/$',
        views.TabelaDePreco.as_view(),
        name='tabela_de_preco__get'),

    re_path(r'^planilha_bling/$',
        views.PlanilhaBling.as_view(),
        name='planilha_bling'),

]

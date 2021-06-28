from django.urls import re_path

from . import views


app_name = 'estoque'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^posicao_estoque/$', views.PosicaoEstoque.as_view(),
        name='posicao_estoque'),

    re_path(r'^valor_mp/$', views.ValorMp.as_view(), name='valor_mp'),

    re_path(r'^refs_com_movimento/$', views.RefsComMovimento.as_view(),
        name='refs_com_movimento'),

    re_path(r'^referencia_deposito/$', views.ReferenciaDeposito.as_view(),
        name='referencia_deposito'),

    re_path(r'^mostra_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<modelo>[^/]+)?/?$',
        views.MostraEstoque.as_view(), name='mostra_estoque__get'),

    re_path(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),
    re_path(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),
    re_path(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/(?P<conf_hash>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),

    re_path(r'^executa_ajuste/(?P<dep>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<ajuste>[^/]+)/'
        r'(?P<num_doc>[^/]+)/(?P<trail>[^/]+)/$',
        views.executa_ajuste, name='executa_ajuste'),

    re_path(r'^estoque_na_data/$', views.EstoqueNaData.as_view(),
        name='estoque_na_data'),

    re_path(r'^confronta_estoque/$', views.ConfrontaEstoque.as_view(),
        name='confronta_estoque'),

    re_path(r'^item_no_tempo/$', views.ItemNoTempo.as_view(),
        name='item_no_tempo'),
    re_path(r'^item_no_tempo/(?P<ref>[^/]+)/(?P<cor>[^/]+)/'
        r'(?P<tam>[^/]+)/(?P<deposito>[^/]+)/$',
        views.ItemNoTempo.as_view(), name='item_no_tempo__get'),

    re_path(r'^transferencia/(?P<tipo>.+)/$', views.Transferencia.as_view(),
        name='transferencia'),

    re_path(r'^lista_movs/$', views.ListaMovimentos.as_view(),
        name='lista_movs'),
    re_path(r'^lista_movs/(?P<num_doc>[^/]+)/$',
        views.ListaMovimentos.as_view(),
        name='lista_movs__get'),

    re_path(r'^lista_docs_mov/$', views.ListaDocsMovimentacao.as_view(),
        name='lista_docs_mov'),

    re_path((r'^ajax/movimenta/'
         r'(?P<tip_mov>.+)/'
         r'(?P<nivel>.+)/'
         r'(?P<ref>.+)/'
         r'(?P<tam>.+)/'
         r'(?P<cor>.+)/'
         r'(?P<quantidade>.+)/'
         r'(?P<deposito_origem>.+)/'
         r'(?P<deposito_destino>.+)/'
         r'(?P<nova_ref>.+)/'
         r'(?P<novo_tam>.+)/'
         r'(?P<nova_cor>.+)/'
         r'(?P<num_doc>.+)/'
         r'(?P<descricao>.+)/'
         r'(?P<cria_num_doc>.+)/'
         r'(?P<executa>.+)/'
         r'$'),
        views.Movimenta.as_view(),
        name='movimenta'),

]

from django.conf.urls import url

from . import views


app_name = 'estoque'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^posicao_estoque/$', views.PosicaoEstoque.as_view(),
        name='posicao_estoque'),

    url(r'^valor_mp/$', views.ValorMp.as_view(), name='valor_mp'),

    url(r'^refs_com_movimento/$', views.RefsComMovimento.as_view(),
        name='refs_com_movimento'),

    url(r'^referencia_deposito/$', views.ReferenciaDeposito.as_view(),
        name='referencia_deposito'),

    url(r'^mostra_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<modelo>[^/]+)?/?$',
        views.MostraEstoque.as_view(), name='mostra_estoque__get'),

    url(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),
    url(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),
    url(r'^edita_estoque/(?P<deposito>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<qtd>[^/]+)/(?P<conf_hash>[^/]+)/$',
        views.EditaEstoque.as_view(), name='edita_estoque__get'),

    url(r'^executa_ajuste/(?P<dep>[^/]+)/(?P<ref>[^/]+)/'
        r'(?P<cor>[^/]+)/(?P<tam>[^/]+)/(?P<ajuste>[^/]+)/'
        r'(?P<num_doc>[^/]+)/(?P<trail>[^/]+)/$',
        views.executa_ajuste, name='executa_ajuste'),

    url(r'^estoque_na_data/$', views.EstoqueNaData.as_view(),
        name='estoque_na_data'),

    url(r'^confronta_estoque/$', views.ConfrontaEstoque.as_view(),
        name='confronta_estoque'),

    url(r'^item_no_tempo/$', views.ItemNoTempo.as_view(),
        name='item_no_tempo'),
    url(r'^item_no_tempo/(?P<ref>[^/]+)/(?P<cor>[^/]+)/'
        r'(?P<tam>[^/]+)/(?P<deposito>[^/]+)/$',
        views.ItemNoTempo.as_view(), name='item_no_tempo__get'),

    url(r'^transferencia/(?P<tipo>.+)/$', views.Transferencia.as_view(),
        name='transferencia'),

    url(r'^lista_movs/$', views.ListaMovimentos.as_view(),
        name='lista_movs'),
    url(r'^lista_movs/(?P<num_doc>[^/]+)/$',
        views.ListaMovimentos.as_view(),
        name='lista_movs__get'),

    url(r'^lista_docs_mov/$', views.ListaDocsMovimentacao.as_view(),
        name='lista_docs_mov'),

    url((r'^ajax/movimenta/'
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

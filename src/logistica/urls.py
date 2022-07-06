from pprint import pprint

from django.urls import (
    path, 
    re_path,
)

from logistica.views import (
    entr_nf_historico,
    main,
    notafiscal_chave,
    etiqueta_nf,
)
from logistica.views.ajax import entr_nf_cadastro
from logistica.views.entrada_nf import lista
from logistica.views.nf import (
    consulta,
    embarcando,
    movimentada,
    numero_nf,
)

__all__ = ['app_name', 'urlpatterns']


app_name = 'logistica'
urlpatterns = [
    re_path(
        r"^$",
        main.index,
        name="index",
    ),
    re_path(
        r"^notafiscal_rel/$",
        consulta.NotafiscalRel.as_view(),
        name="notafiscal_rel",
    ),
    re_path(
        r"^notafiscal_rel/(?P<dia>\d+)/(?P<mes>\d+)/(?P<ano>\d+)/$",
        consulta.NotafiscalRel.as_view(),
        name="notafiscal_rel__get",
    ),
    re_path(
        r"^notafiscal_chave/(?P<chave>\d+)?/?$",
        notafiscal_chave.NotafiscalChave.as_view(),
        name="notafiscal_chave",
    ),
    re_path(
        r"^notafiscal_nf/(?P<nf>\d+)?/?$",
        numero_nf.notafiscal_nf,
        name="notafiscal_nf",
    ),
    re_path(
        r"^notafiscal_embarcando/$",
        embarcando.NotafiscalEmbarcando.as_view(),
        name="notafiscal_embarcando",
    ),
    re_path(
        r"^notafiscal_movimentadas/$",
        movimentada.NotafiscalMovimentadas.as_view(),
        name="notafiscal_movimentadas",
    ),
    re_path(
        r"^entrada_nf/lista/$",
        lista.EntradaNfLista.as_view(),
        name="entr_nf_lista",
    ),
    re_path(
        r"^entrada_nf/historico/(?P<id>[^/]+)/$",
        entr_nf_historico.EntradaNfHistorico.as_view(),
        name="entr_nf_historico",
    ),
    re_path(
        r"^ajax/entr_nf_cadastro/(?P<cadastro>[^/]+)/$",
        entr_nf_cadastro.entr_nf_cadastro,
        name="ajax_entr_nf_cadastro",
    ),
    path(
        'etiqueta_nf/',
        etiqueta_nf.EtiquetaNf.as_view(),
        name='etiqueta_nf',
    ),
]

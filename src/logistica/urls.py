from django.urls import re_path

import logistica.views
import logistica.views.ajax
import logistica.views.entrada_nf


app_name = 'logistica'
urlpatterns = [
    re_path(r"^$", logistica.views.index, name="index"),
    re_path(
        r"^notafiscal_rel/$",
        logistica.views.NotafiscalRel.as_view(),
        name="notafiscal_rel",
    ),
    re_path(
        r"^notafiscal_rel/(?P<dia>\d+)/(?P<mes>\d+)/(?P<ano>\d+)/$",
        logistica.views.NotafiscalRel.as_view(),
        name="notafiscal_rel__get",
    ),
    re_path(
        r"^notafiscal_chave/(?P<chave>\d+)?/?$",
        logistica.views.NotafiscalChave.as_view(),
        name="notafiscal_chave",
    ),
    re_path(
        r"^notafiscal_nf/(?P<nf>\d+)?/?$",
        logistica.views.notafiscal_nf,
        name="notafiscal_nf",
    ),
    re_path(
        r"^notafiscal_embarcando/$",
        logistica.views.NotafiscalEmbarcando.as_view(),
        name="notafiscal_embarcando",
    ),
    re_path(
        r"^notafiscal_movimentadas/$",
        logistica.views.NotafiscalMovimentadas.as_view(),
        name="notafiscal_movimentadas",
    ),
    re_path(
        r"^entrada_nf/_sem_xml/$",
        logistica.views.EntradaNfSemXml.as_view(),
        name="entr_nf_sem_xml",
    ),
    re_path(
        r"^entrada_nf/lista/$",
        logistica.views.entrada_nf.EntradaNfLista.as_view(),
        name="entr_nf_lista",
    ),
    re_path(
        r"^entrada_nf/historico/(?P<id>[^/]+)/$",
        logistica.views.EntradaNfHistorico.as_view(),
        name="entr_nf_historico",
    ),
    re_path(
        r"^ajax/entr_nf_cadastro/(?P<cadastro>[^/]+)/$",
        logistica.views.ajax.entr_nf_cadastro,
        name="ajax_entr_nf_cadastro",
    ),
]

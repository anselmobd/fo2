from django.conf.urls import url

import logistica.views
import logistica.views.ajax


app_name = 'logistica'
urlpatterns = [
    url(r"^$", logistica.views.index, name="index"),
    url(
        r"^notafiscal_rel/$",
        logistica.views.NotafiscalRel.as_view(),
        name="notafiscal_rel",
    ),
    url(
        r"^notafiscal_rel/(?P<dia>\d+)/(?P<mes>\d+)/(?P<ano>\d+)/$",
        logistica.views.NotafiscalRel.as_view(),
        name="notafiscal_rel__get",
    ),
    url(
        r"^notafiscal_chave/(?P<chave>\d+)?/?$",
        logistica.views.NotafiscalChave.as_view(),
        name="notafiscal_chave",
    ),
    url(
        r"^notafiscal_nf/(?P<nf>\d+)?/?$",
        logistica.views.notafiscal_nf,
        name="notafiscal_nf",
    ),
    url(
        r"^notafiscal_embarcando/$",
        logistica.views.NotafiscalEmbarcando.as_view(),
        name="notafiscal_embarcando",
    ),
    url(
        r"^notafiscal_movimentadas/$",
        logistica.views.NotafiscalMovimentadas.as_view(),
        name="notafiscal_movimentadas",
    ),
    url(
        r"^entrada_nf/_sem_xml/$",
        logistica.views.EntradaNfSemXml.as_view(),
        name="entr_nf_sem_xml",
    ),
    url(
        r"^entrada_nf/lista/$",
        logistica.views.EntradaNfLista.as_view(),
        name="entr_nf_lista",
    ),
    url(
        r"^entrada_nf/historico/(?P<id>[^/]+)/$",
        logistica.views.EntradaNfHistorico.as_view(),
        name="entr_nf_historico",
    ),
    url(
        r"^ajax/entr_nf_cadastro/(?P<cadastro>[^/]+)/$",
        logistica.views.ajax.entr_nf_cadastro,
        name="ajax_entr_nf_cadastro",
    ),
]

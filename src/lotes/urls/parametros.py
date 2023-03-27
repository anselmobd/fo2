from django.urls import path, re_path, include

from lotes.views.parametros import (
    lead_colecao,
    lote_caixa,
    lote_min_colecao,
    lote_min_tamanho,
)


def name(name):
    return f"parametros-{name}"


urlpatterns = [
    re_path(
        r"^lead_colecao/(?P<id>[^/]+)?$",
        lead_colecao.LeadColecao.as_view(),
        name=name('lead_colecao'),
    ),
    re_path(
        r"^lote_min_colecao/(?P<id>[^/]+)?$",
        lote_min_colecao.LoteMinColecao.as_view(),
        name=name('lote_min_colecao'),
    ),
    re_path(
        r"^regras_lote_caixa/",
        include([
            path(
                "",
                lote_caixa.LoteCaixa.as_view(),
                name=name('regras_lote_caixa'),
            ),
            re_path(
                r"(?P<colecao>[0-9\-]+)/(?P<referencia>[A-Z0-9\-]+)/(?P<ead>[ead])/$",
                lote_caixa.LoteCaixa.as_view(),
                name=name('regras_lote_caixa'),
            ),
        ]),
    ),
    re_path(
        r"^regras_lote_min_tamanho/(?P<id>[^/]+)?$",
        lote_min_tamanho.LoteMinTamanho.as_view(),
        name=name('regras_lote_min_tamanho'),
    ),
]

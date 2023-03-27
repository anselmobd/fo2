from django.urls import path, re_path

from lotes.views.parametros import (
    lead_colecao,
    lote_min_colecao,
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
]

from django.urls import path, re_path

from lotes.views.parametros import (
    lead_colecao,
)


def name(name):
    return f"parametros-{name}"


urlpatterns = [
    re_path(
        r"^lead_colecao/(?P<id>[^/]+)?$",
        lead_colecao.LeadColecao.as_view(),
        name=name('lead_colecao'),
    ),
]

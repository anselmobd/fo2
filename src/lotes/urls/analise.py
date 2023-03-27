from django.urls import path, re_path

from lotes.views.analise import (
    dtcorte_alter,
)


def name(name):
    return f"analise-{name}"


urlpatterns = [
    re_path(
        r"^marca_dtcorte_alterop_cortada/(?P<data>[^/]+)?$",
        dtcorte_alter.DtCorteAlter.as_view(),
        name=name('dtcorte_alter'),
    ),
]

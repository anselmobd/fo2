from django.urls import path, re_path

from lotes.views.analise import (
    cd_bonus,
    dtcorte_alter,
)


def name(name):
    return f"analise-{name}"


urlpatterns = [
    re_path(
        r"^dtcorte_alter/(?P<data>[^/]+)?$",
        dtcorte_alter.DtCorteAlter.as_view(),
        name=name('dtcorte_alter'),
    ),
    re_path(
        r"^cd_bonus/(?P<data>[^/]+)?$",
        cd_bonus.CdBonusView.as_view(),
        name=name('cd_bonus'),
    ),
]

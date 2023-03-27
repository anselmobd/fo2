from django.urls import path

from lotes.views.impressao import (
    imprime_caixa_lotes,
    imprime_lotes,
    imprime_ob1,
    imprime_tag,
)


def name(name):
    return f"impressao-{name}"


urlpatterns = [
    path(
        "imprime_caixa_lotes/",
        imprime_caixa_lotes.ImprimeCaixaLotes.as_view(),
        name=name('imprime_caixa_lotes'),
    ),
    path(
        "imprime_lotes/",
        imprime_lotes.ImprimeLotes.as_view(),
        name=name('imprime_lotes'),
    ),
    path(
        "imprime_ob1/",
        imprime_ob1.ImprimeOb1.as_view(),
        name=name('imprime_ob1'),
    ),
    path(
        "imprime_tag/",
        imprime_tag.ImprimeTag.as_view(),
        name=name('imprime_tag'),
    ),
]

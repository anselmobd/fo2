from django.urls import path, re_path, include

from lotes.views.impressao import (
    imprime_lotes,
)


def name(name):
    return f"impressao-{name}"


urlpatterns = [
    path(
        "imprime_lotes/",
        imprime_lotes.ImprimeLotes.as_view(),
        name=name('imprime_lotes'),
    ),
]

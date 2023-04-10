from django.urls import path

from produto.views.tag.pesquisa import *


def name(name):
    return f"tag-{name}"


urlpatterns = [
    path(
        "pesquisa/",
        TagPesquisaView.as_view(),
        name=name('pesquisa'),
    ),
]

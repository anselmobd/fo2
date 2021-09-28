from django.urls import re_path

import ti.views


app_name = 'ti'
urlpatterns = [
    re_path(r'^$', ti.views.views.index, name='index'),
    re_path(
        r'^equipamento_lista$',
        ti.views.lista.EquipamentoLista.as_view(),
        name='equipamento_lista'),
]

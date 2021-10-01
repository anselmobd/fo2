from django.urls import re_path

import itat.views


app_name = 'itat'
urlpatterns = [
    re_path(r'^$', itat.views.views.index, name='index'),

    re_path(
        r'^equipamento_lista$',
        itat.views.equipamento_lista.EquipamentoLista.as_view(),
        name='equipamento_lista'),
]

from django.urls import re_path

from base.views import (
    testa_db,
    usuarios,
    views,
)


app_name = 'base'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^usuarios/$', usuarios.Usuarios.as_view(), name='usuarios'),

    re_path(r'^testa_db/$', testa_db.TestaDB.as_view(), name='testa_db'),

]

from django.urls import re_path

import base.views as views
from base.views import usuarios


app_name = 'base'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^usuarios/$', usuarios.Usuarios.as_view(), name='usuarios'),

    re_path(r'^testa_db/$', views.TestaDB.as_view(), name='testa_db'),

]

from django.conf.urls import url

import base.views as views


app_name = 'base'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^usuarios/$', views.Usuarios.as_view(), name='usuarios'),

    url(r'^testa_db/$', views.TestaDB.as_view(), name='testa_db'),

]

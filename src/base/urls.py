from django.conf.urls import url

import base.views as views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^usuarios/$', views.Usuarios.as_view(), name='usuarios'),

]

from django.conf.urls import url

import cd.views as views

urlpatterns = [

    url(r'^$', views.Mapa.as_view(), name='index'),

]

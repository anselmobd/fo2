from django.conf.urls import url

import cd.views as views


app_name = 'mapa'
urlpatterns = [

    url(r'^$', views.Mapa.as_view(), name='index'),

]

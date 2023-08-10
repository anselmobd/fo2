from django.urls import re_path

import cd.views as views


app_name = 'mapa'
urlpatterns = [

    re_path(r'^$', views.Mapa.as_view(), name='index'),

]

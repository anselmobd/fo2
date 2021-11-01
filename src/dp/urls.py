from django.urls import re_path

from . import views


app_name = 'dp'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^gera_movi_premio/$', views.GeraMoviPremio.as_view(), name='gera_movi_premio'),
]

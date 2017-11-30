from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='rh'),
    url(r'^campanhas/$', views.campanhas, name='rh_campanhas'),
    url(r'^datas/$', views.datas, name='rh_datas'),
]

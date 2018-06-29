from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='rh'),
    url(r'^campanhas/$', views.campanhas, name='rh_campanhas'),
    url(r'^datas/$', views.datas, name='rh_datas'),
    url(r'^fotos/$', views.fotos, name='rh_fotos'),
    url(r'^videos/$', views.videos, name='rh_videos'),
    url(r'^fotos_homenagem20180614/$', views.fotos_homenagem20180614,
        name='rh_fotos_homenagem20180614'),
    url(r'^fotos_brigadista2018/$', views.fotos_brigadista2018,
        name='rh_fotos_brigadista2018'),
    url(r'^videos_brigadista2018/$', views.videos_brigadista2018,
        name='rh_videos_brigadista2018'),
]

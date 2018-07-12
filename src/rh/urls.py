from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^campanhas/$', views.campanhas, name='campanhas'),

    url(r'^datas/$', views.datas, name='datas'),

    url(r'^fotos/$', views.fotos, name='fotos'),

    url(r'^videos/$', views.videos, name='videos'),

    url(r'^fotos_homenagem20180614/$', views.fotos_homenagem20180614,
        name='fotos_homenagem20180614'),

    url(r'^fotos_brigadista2018/$', views.fotos_brigadista2018,
        name='fotos_brigadista2018'),

    url(r'^videos_brigadista2018/$', views.videos_brigadista2018,
        name='videos_brigadista2018'),
]

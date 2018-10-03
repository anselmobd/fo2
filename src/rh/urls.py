from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^campanhas/$', views.campanhas, name='campanhas'),

    url(r'^datas/$', views.datas, name='datas'),

    url(r'^mensagens/$', views.mensagens, name='mensagens'),

    url(r'^fotos/$', views.fotos, name='fotos'),

    url(r'^videos/$', views.videos, name='videos'),

    url(r'^fotos_homenagem20180614/$', views.fotos_homenagem20180614,
        name='fotos_homenagem20180614'),

    url(r'^fotos_brigadista2018/$', views.fotos_brigadista2018,
        name='fotos_brigadista2018'),

    url(r'^videos_brigadista2018/$', views.videos_brigadista2018,
        name='videos_brigadista2018'),

    url(r'^20180720_dia_do_amigo/$', views.fotos_20180720_dia_do_amigo,
        name='20180720_dia_do_amigo'),

    url(r'^aniversariantes/$',
        views.aniversariantes, name='aniversariantes_now'),
    url(r'^aniversariantes/(?P<ano>\d{4})/(?P<mes>\d{1,2})/?$',
        views.aniversariantes, name='aniversariantes'),
]

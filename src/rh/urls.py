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

    url(r'^2018_dia_rosa_fotos/$', views.v2018_dia_rosa_fotos,
        name='2018_dia_rosa_fotos'),

    url(r'^2018_dia_rosa_videos/$', views.v2018_dia_rosa_videos,
        name='2018_dia_rosa_videos'),

    url(r'^20180720_dia_do_amigo/$', views.fotos_20180720_dia_do_amigo,
        name='20180720_dia_do_amigo'),

    url(r'^fotos_2019_04_01_1o_cafe/$', views.fotos_2019_04_01_1o_cafe,
        name='fotos_2019_04_01_1o_cafe'),

    url(r'^fotos_2019_03_lorena/$', views.fotos_2019_03_lorena,
        name='fotos_2019_03_lorena'),

    url(r'^fotos_2019_05_24_bianca/$', views.fotos_2019_05_24_bianca,
        name='fotos_2019_05_24_bianca'),

    url(r'^media_2019_04_09_dicas/$', views.media_2019_04_09_dicas,
        name='media_2019_04_09_dicas'),

    url(r'^divulga_atitudes_crise/$', views.divulga_atitudes_crise,
        name='divulga_atitudes_crise'),

    url(r'^aniversariantes/$',
        views.aniversariantes, name='aniversariantes_now'),
    url(r'^aniversariantes/(?P<ano>\d{4})/(?P<mes>\d{1,2})/?$',
        views.aniversariantes, name='aniversariantes'),
]

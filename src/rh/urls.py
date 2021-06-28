from django.urls import re_path

from . import views


app_name = 'rh'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^principal$', views.principal, name='principal'),

    re_path(r'^campanhas/(?P<id>.+)?/?$',
        views.campanhas, name='campanhas'),

    re_path(r'^eventos/(?P<id>.+)?/?$',
        views.eventos, name='eventos'),

    re_path(r'^comunicados/(?P<id>.+)?/?$',
        views.comunicados, name='comunicados'),

    re_path(r'^datas/(?P<data>.+)/$', views.datas, name='datas'),

    re_path(r'^fotos/$', views.fotos, name='fotos'),

    re_path(r'^videos/$', views.videos, name='videos'),

    re_path(r'^fotos_homenagem20180614/$', views.fotos_homenagem20180614,
        name='fotos_homenagem20180614'),

    re_path(r'^fotos_brigadista2018/$', views.fotos_brigadista2018,
        name='fotos_brigadista2018'),

    re_path(r'^videos_brigadista2018/$', views.videos_brigadista2018,
        name='videos_brigadista2018'),

    re_path(r'^2018_dia_rosa_fotos/$', views.v2018_dia_rosa_fotos,
        name='2018_dia_rosa_fotos'),

    re_path(r'^2018_dia_rosa_videos/$', views.v2018_dia_rosa_videos,
        name='2018_dia_rosa_videos'),

    re_path(r'^20180720_dia_do_amigo/$', views.fotos_20180720_dia_do_amigo,
        name='20180720_dia_do_amigo'),

    re_path(r'^fotos_2019_04_01_1o_cafe/$', views.fotos_2019_04_01_1o_cafe,
        name='fotos_2019_04_01_1o_cafe'),

    re_path(r'^fotos_2019_03_lorena/$', views.fotos_2019_03_lorena,
        name='fotos_2019_03_lorena'),

    re_path(r'^fotos_2019_05_24_bianca/$', views.fotos_2019_05_24_bianca,
        name='fotos_2019_05_24_bianca'),

    re_path(r'^fotos_2019_06_14_adriana_leo/$', views.fotos_2019_06_14_adriana_leo,
        name='fotos_2019_06_14_adriana_leo'),

    re_path(r'^fotos_2019_07_12_brigadistas_2019/$',
        views.fotos_2019_07_12_brigadistas_2019,
        name='fotos_2019_07_12_brigadistas_2019'),

    re_path(r'^media_2019_04_09_dicas/$', views.media_2019_04_09_dicas,
        name='media_2019_04_09_dicas'),

    re_path(r'^media_2019_07_16_sobre_amizade/$',
        views.media_2019_07_16_sobre_amizade,
        name='media_2019_07_16_sobre_amizade'),

    re_path(r'^media_2019_08_01_25_anos/$',
        views.media_2019_08_01_25_anos,
        name='media_2019_08_01_25_anos'),

    re_path(r'^divulga_atitudes_crise/$', views.divulga_atitudes_crise,
        name='divulga_atitudes_crise'),

]

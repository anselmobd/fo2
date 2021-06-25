from django.conf.urls import url

from . import views


app_name = 'rh'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^principal$', views.principal, name='principal'),

    url(r'^campanhas/(?P<id>.+)?/?$',
        views.campanhas, name='campanhas'),

    url(r'^eventos/(?P<id>.+)?/?$',
        views.eventos, name='eventos'),

    url(r'^comunicados/(?P<id>.+)?/?$',
        views.comunicados, name='comunicados'),

    url(r'^datas/(?P<data>.+)/$', views.datas, name='datas'),

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

    url(r'^fotos_2019_06_14_adriana_leo/$', views.fotos_2019_06_14_adriana_leo,
        name='fotos_2019_06_14_adriana_leo'),

    url(r'^fotos_2019_07_12_brigadistas_2019/$',
        views.fotos_2019_07_12_brigadistas_2019,
        name='fotos_2019_07_12_brigadistas_2019'),

    url(r'^media_2019_04_09_dicas/$', views.media_2019_04_09_dicas,
        name='media_2019_04_09_dicas'),

    url(r'^media_2019_07_16_sobre_amizade/$',
        views.media_2019_07_16_sobre_amizade,
        name='media_2019_07_16_sobre_amizade'),

    url(r'^media_2019_08_01_25_anos/$',
        views.media_2019_08_01_25_anos,
        name='media_2019_08_01_25_anos'),

    url(r'^divulga_atitudes_crise/$', views.divulga_atitudes_crise,
        name='divulga_atitudes_crise'),

]

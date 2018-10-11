from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ref/$', views.Ref.as_view(), name='ref'),
    url(r'^ref/(?P<item>[29]?\.?.{5})/$', views.Ref.as_view(),
        name='ref__get'),

    url(r'^busca/$', views.Busca.as_view(),
        name='busca'),
    url(r'^busca/(?P<busca>.+)/$', views.Busca.as_view(),
        name='busca__get'),

    url(r'^rolo/(?P<barcode>.+)/(?P<origem>.+)/$', views.rolo_json,
        name='rolo_json'),

    url(r'^rolos_bipados/$', views.RolosBipados.as_view(),
        name='rolos_bipados'),

    url(r'^bipa_rolo/$', views.BipaRolo.as_view(),
        name='bipa_rolo'),

    url(r'^necessidade/$', views.Necessidade.as_view(),
        name='necessidade'),

    url(r'^receber/$', views.Receber.as_view(),
        name='receber'),

    url(r'^estoque/$', views.Estoque.as_view(),
        name='estoque'),

    url(r'^mapa_por_ref/$', views.MapaPorRefs.as_view(),
        name='mapa_por_ref'),

    url(r'^mapa/(?P<nivel>[29])/(?P<ref>.{5})/(?P<cor>.{6})/(?P<tam>.{1,3})/$',
        views.MapaPorInsumo.as_view(),
        name='mapa'),

    url(r'^mapa_necessidade_detalhe/(?P<nivel>[29])/(?P<ref>.{5})/'
        '(?P<cor>.{6})/(?P<tam>.{1,3})/(?P<semana>.*)/$',
        views.MapaNecessidadeDetalhe.as_view(),
        name='mapa_necessidade_detalhe'),

    url(r'^previsao/$', views.Previsao.as_view(),
        name='previsao'),

    url(r'^necessidade_1_previsao/(?P<periodo>.{4})/$',
        views.Necessidade1Previsao.as_view(),
        name='necessidade_1_previsao'),

    url(r'^necessidades_previsoes/$', views.NecessidadesPrevisoes.as_view(),
        name='necessidades_previsoes'),

    url(r'^mapa_por_sem/$', views.MapaPorSemana.as_view(),
        name='mapa_por_sem'),
    url(r'^mapa_por_sem/(?P<periodo>\d{1,4})/(?P<qtd_semanas>\d{1,2})/?$',
        views.MapaPorSemana.as_view(),
        name='mapa_por_sem__get'),
    url(r'^mapa_por_sem_ref/(?P<item>(?:.{2}|\d\..{5}\..{6}\..{1,3}))/'
        '(?P<dtini>\d{8})/(?P<nsem>\d{1,2})/$',
        views.mapa_sem_ref,
        name='mapa_por_sem_ref__get'),

    url(r'^mapa_por_semana/$', views.MapaPorSemanaNew.as_view(),
        name='mapa_por_semana'),
    url(r'^mapa_por_semana/(?P<periodo>\d{1,4})/(?P<qtd_semanas>\d{1,2})/?$',
        views.MapaPorSemanaNew.as_view(),
        name='mapa_por_semana__get'),
    url(r'^mapa_por_semana_ref/(?P<item>(?:.{2}|\d\..{5}\..{6}\..{1,3}))/'
        '(?P<dtini>\d{8})/$',
        views.mapa_sem_ref_new,
        name='mapa_por_semana_ref__get'),

    url(r'^roloinfo/$', views.Rolo.as_view(), name='rolo'),
    url(r'^roloinfo/(?P<rolo>[29]?\.?.{5})/$', views.Rolo.as_view(),
        name='rolo__get'),
]

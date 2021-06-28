from django.urls import re_path

from . import views


app_name = 'insumo'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^ref/$', views.Ref.as_view(), name='ref'),
    re_path(r'^ref/(?P<item>[29]?\.?.{5})/$', views.Ref.as_view(),
        name='ref__get'),

    re_path(r'^busca/$', views.Busca.as_view(),
        name='busca'),
    re_path(r'^busca/(?P<busca>.+)/$', views.Busca.as_view(),
        name='busca__get'),

    re_path(r'^rolo/(?P<barcode>.+)/(?P<origem>.+)/$', views.rolo_json,
        name='rolo_json'),

    re_path(r'^rolos_bipados/$', views.RolosBipados.as_view(),
        name='rolos_bipados'),

    re_path(r'^bipa_rolo/$', views.BipaRolo.as_view(),
        name='bipa_rolo'),

    re_path(r'^necessidade/$', views.Necessidade.as_view(),
        name='necessidade'),

    re_path(r'^receber/$', views.Receber.as_view(),
        name='receber'),

    re_path(r'^estoque/$', views.Estoque.as_view(),
        name='estoque'),

    re_path(r'^mapa_por_ref/$', views.MapaPorRefs.as_view(),
        name='mapa_por_ref'),

    re_path(r'^mapa/(?P<nivel>[29])/(?P<ref>.{5})/(?P<cor>.{6})/'
        r'(?P<tam>.{1,3})/$',
        views.MapaPorInsumo.as_view(),
        name='mapa'),
    re_path(r'^mapa_calc/(?P<nivel>[29])/(?P<ref>.{5})/(?P<cor>.{6})/'
        r'(?P<tam>.{1,3})/$',
        views.MapaPorInsumoCalc.as_view(),
        name='mapa_calc'),

    re_path(r'^mapa_necessidade_detalhe/(?P<nivel>[29])/(?P<ref>.{5})/'
        r'(?P<cor>.{6})/(?P<tam>.{1,3})/(?P<semana>.*)/$',
        views.MapaNecessidadeDetalhe.as_view(),
        name='mapa_necessidade_detalhe'),
    re_path(r'^mapa_necessidade_detalhe_old/(?P<nivel>[29])/(?P<ref>.{5})/'
        r'(?P<cor>.{6})/(?P<tam>.{1,3})/(?P<semana>.*)/$',
        views.MapaNecessidadeDetalheOld.as_view(),
        name='mapa_necessidade_detalhe_old'),

    re_path(r'^previsao/$', views.Previsao.as_view(),
        name='previsao'),

    re_path(r'^necessidade_1_previsao/(?P<periodo>.{4})/$',
        views.Necessidade1Previsao.as_view(),
        name='necessidade_1_previsao'),

    re_path(r'^necessidades_previsoes/$', views.NecessidadesPrevisoes.as_view(),
        name='necessidades_previsoes'),

    re_path(r'^mapa_por_sem/$', views.MapaPorSemana.as_view(),
        name='mapa_por_sem'),
    re_path(r'^mapa_por_sem/(?P<periodo>\d{1,4})/(?P<qtd_semanas>\d{1,2})/?$',
        views.MapaPorSemana.as_view(),
        name='mapa_por_sem__get'),
    re_path(r'^mapa_por_sem_ref/(?P<item>(?:.{2}|\d\..{5}\..{6}\..{1,3}))/'
        r'(?P<dtini>\d{8})/(?P<nsem>\d{1,2})/$',
        views.mapa_sem_ref,
        name='mapa_por_sem_ref__get'),

    re_path(r'^mapa_semanal/$',
        views.MapaSemanal.as_view(),
        name='mapa_semanal'),
    re_path(r'^mapa_semanal/(?P<periodo>\d{1,4})/?$',
        views.MapaSemanal.as_view(),
        name='mapa_semanal__get'),

    re_path(r'^rolo/$', views.Rolo.as_view(), name='rolo'),
    re_path(r'^rolo/(?P<rolo>[29]?\.?.{5})/$', views.Rolo.as_view(),
        name='rolo__get'),

    re_path(r'^mapa_compras_semana/$', views.MapaComprasSemana.as_view(),
        name='mapa_compras_semana'),

    re_path(r'^mapa_compras_semana_ref/(?P<item>(?:.{2}|\d\..{5}\..{6}\..{1,3}))/'
        r'(?P<dtini>\d{8})/(?P<qtdsem>(?:\d{1,2}|--))/$',
        views.mapa_compras_semana_ref,
        name='mapa_compras_semana_ref__get'),

    re_path(r'^mapa_compras/(?P<nivel>[29])/(?P<ref>.{5})/(?P<cor>.{6})/'
        r'(?P<tam>.{1,3})/$',
        views.MapaCompras.as_view(),
        name='mapa_compras'),
    re_path(r'^mapa_compras_calc/(?P<nivel>[29])/(?P<ref>.{5})/(?P<cor>.{6})/'
        r'(?P<tam>.{1,3})/$',
        views.MapaComprasCalc.as_view(),
        name='mapa_compras_calc'),

    re_path(r'^mapa_compras_necessidades/$',
        views.MapaComprasNecessidades.as_view(),
        name='mapa_compras_necessidades'),
    re_path(r'^mapa_compras_necessidades/(?P<nivel>[29])/(?P<ref>.{5})/'
        r'(?P<cor>.{6})/(?P<tamanho>.{1,3})/(?P<colunas>.)/$',
        views.MapaComprasNecessidades.as_view(),
        name='mapa_compras_necessidades__get'),

    re_path(r'^mapa_compras_necessidade_detalhe/(?P<nivel>[29])/(?P<ref>.{5})/'
        r'(?P<cor>.{6})/(?P<tam>.{1,3})/(?P<semana>.*)/$',
        views.MapaComprasNecessidadeDetalhe.as_view(),
        name='mapa_compras_necessidade_detalhe'),
]

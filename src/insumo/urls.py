from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='insumo'),

    url(r'^ref/$', views.Ref.as_view(), name='mp_ref'),
    url(r'^ref/(?P<item>[29]?\.?.{5})/$',
        views.Ref.as_view(), name='mp_ref_ref'),

    url(r'^lista_insumo/$', views.ListaInsumo.as_view(),
        name='lista_insumo'),
    url(r'^lista_insumo/(?P<busca>.+)/$', views.ListaInsumo.as_view(),
        name='lista_insumo_busca'),

    url(r'^rolo/(?P<barcode>.+)/(?P<origem>.+)/$',
        views.rolo_json, name='mp_rolo_json'),

    url(r'^rolos_bipados/$', views.RolosBipados.as_view(),
        name='rolos_bipados'),

    url(r'^necessidade/$', views.Necessidade.as_view(),
        name='insumo_necessidade'),

    url(r'^receber/$', views.Receber.as_view(),
        name='insumo_receber'),

    url(r'^estoque/$', views.Estoque.as_view(),
        name='insumo_estoque'),

    url(r'^mapa_ref/$', views.MapaRefs.as_view(),
        name='insumo_mapa_ref'),

    url(r'^mapa/(?P<nivel>[29])/(?P<ref>.{5})/(?P<cor>.{6})/(?P<tam>.{1,3})/$',
        views.Mapa.as_view(), name='insumo_mapa'),

    url(r'^necessidade_detalhe/(?P<nivel>[29])/(?P<ref>.{5})/'
        '(?P<cor>.{6})/(?P<tam>.{1,3})/(?P<semana>.*)/$',
        views.MapaNecessidadeDetalhe.as_view(),
        name='insumo_necessidade_detalhe'),

    url(r'^previsao/$', views.Previsao.as_view(),
        name='insumo_previsao'),

    url(r'^necessidade_1_previsao/(?P<periodo>.{4})/$',
        views.Necessidade1Previsao.as_view(),
        name='insumo_necessidade_1_previsao'),

    url(r'^necessidades_previsoes/$', views.NecessidadesPrevisoes.as_view(),
        name='insumo_necessidades_previsoes'),

]

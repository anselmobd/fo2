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

    url(r'^mapa/$', views.Mapa.as_view(),
        name='insumo_mapa'),

]

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
]

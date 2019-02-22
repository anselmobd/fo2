from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ref/$', views.Ref.as_view(), name='ref'),
    url(r'^ref/(?P<ref>.+)/$', views.Ref.as_view(), name='ref__get'),

    url(r'^modelo/$', views.Modelo.as_view(), name='modelo'),
    url(r'^modelo/(?P<modelo>.+)/$', views.Modelo.as_view(),
        name='modelo__get'),

    url(r'^gtin/$', views.Gtin.as_view(), name='gtin'),

    url(r'^busca/$', views.Busca.as_view(),
        name='busca'),
    url(r'^busca/(?P<busca>.+)/$', views.Busca.as_view(),
        name='busca__get'),

    url(r'^estr_estagio_de_insumo/$', views.EstrEstagioDeInsumo.as_view(),
        name='estr_estagio_de_insumo'),

    url(r'^estatistica/$', views.estatistica, name='estatistica'),

    url(r'^lista_item_n1_sem_preco_medio/$',
        views.lista_item_n1_sem_preco_medio,
        name='lista_item_n1_sem_preco_medio'),

    url(r'^ajax/stat_nivel/$', views.stat_nivel, name='stat_nivel'),

    url(r'^ajax/stat_niveis/([129]{1}.*)/$',
        views.stat_niveis, name='stat_niveis'),

    url(r'^gera_roteiros_ref/(?P<ref>[^/]+)?/?$',
        views.GeraRoteirosRef.as_view(), name='gera_roteiros_ref'),
]

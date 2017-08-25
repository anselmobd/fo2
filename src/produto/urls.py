from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ref/$', views.Ref.as_view(), name='ref'),
    url(r'^ref/(?P<ref>.+)/$', views.Ref.as_view(), name='ref_ref'),

    url(r'^estatistica/$', views.estatistica, name='estatistica'),
    url(r'^lista_item_n1_sem_preco_medio/$',
        views.lista_item_n1_sem_preco_medio,
        name='lista_item_n1_sem_preco_medio'),
    url(r'^ajax/stat_nivel/$', views.stat_nivel, name='stat_nivel'),
    url(r'^ajax/stat_niveis/([129]{1}.*)/$',
        views.stat_niveis, name='stat_niveis'),
]

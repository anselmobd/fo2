from django.urls import re_path

from . import views


app_name = 'beneficia'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^ob/$', views.Ob.as_view(), name='ob'),
    re_path(r'^ob/(?P<ob>\d+)/$', views.Ob.as_view(), name='ob__get'),

    re_path(r'^busca_ob/$', views.BuscaOb.as_view(), name='busca_ob'),

    re_path(r'^ot/$', views.Ot.as_view(), name='ot'),
    re_path(r'^ot/(?P<ot>\d+)/$', views.Ot.as_view(), name='ot__get'),

    re_path(r'^receita/(?P<ref>.+)?/?$', views.Receita.as_view(), name='receita'),

    re_path(r'^receita_estrutura/(?P<item>.+)?/?$', views.ReceitaEstrutura.as_view(), name='receita_estrutura'),
]

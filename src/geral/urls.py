from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^deposito/$', views.deposito, name='deposito'),
    url(r'^estagio/$', views.estagio, name='estagio'),
    url(r'^painel/(?P<painel>[^/]*)/?$',
        views.PainelView.as_view(), name='ger_painel'),
    url(r'^informativo/(?P<modulo>[^/]+)/(?P<id>[^/]+)?/?$',
        views.InformativoView.as_view(), name='ger_informativo_modulo'),
    url(r'^pop/$', views.pop, name='pop'),
    url(r'^pop/(?P<id>\d+)/?$', views.pop, name='pop_id'),
]

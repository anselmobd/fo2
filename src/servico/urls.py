from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ordens/$',
        views.Ordens.as_view(), name='ordens'),

    url(r'^ordem/$',
        views.Ordem.as_view(), name='ordem'),
    url(r'^ordem/(?P<ordem>\d+)/$',
        views.Ordem.as_view(), name='ordem__get'),

    url(r'^cria_ordem/$',
        views.CriaOrdem.as_view(), name='cria_ordem'),

]

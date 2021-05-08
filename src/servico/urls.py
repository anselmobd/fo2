from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ordens/$',
        views.Lista.as_view(), name='ordens'),

    url(r'^ordem/$',
        views.Ordem.as_view(), name='ordem'),
    url(r'^ordem/(?P<documento>\d+)/$',
        views.Ordem.as_view(), name='ordem__get'),

    url(r'^cria_ordem/$',
        views.CriaOrdem.as_view(), name='cria_ordem'),

    url(r'^edita_ordem/(?P<evento>.+)/(?P<documento>.+)/$',
        views.EditaOrdem.as_view(), name='edita_ordem'),

    url(r'^painel/$',
        views.Painel.as_view(), name='painel'),

]

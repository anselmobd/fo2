from django.urls import re_path

from . import views


app_name = 'servico'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^ordens/$',
        views.Lista.as_view(), name='ordens'),

    re_path(r'^ordem/$',
        views.Ordem.as_view(), name='ordem'),
    re_path(r'^ordem/(?P<documento>\d+)/$',
        views.Ordem.as_view(), name='ordem__get'),

    re_path(r'^cria_ordem/$',
        views.CriaOrdem.as_view(), name='cria_ordem'),

    re_path(r'^edita_ordem/(?P<evento>.+)/(?P<documento>.+)/$',
        views.EditaOrdem.as_view(), name='edita_ordem'),

    re_path(r'^painel/$',
        views.Painel.as_view(), name='painel'),

]

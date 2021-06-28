from django.urls import re_path

from . import views


app_name = 'persona'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^aniversariantes/$',
        views.aniversariantes, name='aniversariantes_now'),
    re_path(r'^aniversariantes/(?P<ano>\d{4})/(?P<mes>\d{1,2})/?$',
        views.aniversariantes, name='aniversariantes'),

    re_path(r'^cria_usuario/$', views.CriaUsuario.as_view(), name='cria_usuario'),

]

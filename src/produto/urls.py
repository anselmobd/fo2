from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/stat_nivel/$', views.stat_nivel, name='stat_nivel'),
    url(r'^ajax/stat_niveis/([129]{1}.*)/$',
        views.stat_niveis, name='stat_niveis'),
]

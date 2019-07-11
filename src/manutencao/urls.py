from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^maquinas/$',
        views.Maquinas.as_view(), name='maquinas'),
]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^rotinas/$',
        views.Rotinas.as_view(), name='rotinas'),
]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^infadprod/(?P<pedido>.+)?/?$',
        views.InfAdProd.as_view(), name='infadprod'),

    url(r'^remeindu/$', views.RemessaIndustr.as_view(), name='remeindu'),

    url(r'^remeindunf/$', views.RemessaIndustrNF.as_view(), name='remeindunf'),
]

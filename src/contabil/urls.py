from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^infadprod/$', views.InfAdProd.as_view(), name='infadprod'),

    url(r'^remeindu/$', views.RemessaIndustr.as_view(), name='remeindu'),
]

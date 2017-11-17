from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='contabil'),
    url(r'^infadprod/$', views.InfAdProd.as_view(), name='infadprod'),
]

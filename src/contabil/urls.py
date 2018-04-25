from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='contabil'),
    url(r'^infadprod/$', views.InfAdProd.as_view(), name='contabil_infadprod'),
    url(r'^remeindu/$', views.RemessaIndustr.as_view(),
        name='contabil_remeindu'),
]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^notafiscal_rel/$',
        views.NotafiscalRel.as_view(), name='notafiscal_rel'),
    url(r'^notafiscal_rel/(?P<data>\d+)/$',
        views.NotafiscalRel.as_view(), name='notafiscal_rel_dt'),
]

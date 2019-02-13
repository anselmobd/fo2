from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^notafiscal_rel/$',
        views.NotafiscalRel.as_view(), name='notafiscal_rel'),
    url(r'^notafiscal_rel/(?P<dia>\d+)/(?P<mes>\d+)/(?P<ano>\d+)/$',
        views.NotafiscalRel.as_view(), name='notafiscal_rel__get'),

    url(r'^notafiscal_chave/$',
        views.NotafiscalChave.as_view(), name='notafiscal_chave'),
]

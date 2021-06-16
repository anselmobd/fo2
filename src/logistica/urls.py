from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^notafiscal_rel/$',
        views.NotafiscalRel.as_view(), name='notafiscal_rel'),
    url(r'^notafiscal_rel/(?P<dia>\d+)/(?P<mes>\d+)/(?P<ano>\d+)/$',
        views.NotafiscalRel.as_view(), name='notafiscal_rel__get'),

    url(r'^notafiscal_chave/(?P<chave>\d+)?/?$',
        views.NotafiscalChave.as_view(), name='notafiscal_chave'),

    url(r'^notafiscal_nf/(?P<nf>\d+)?/?$',
        views.notafiscal_nf, name='notafiscal_nf'),

    url(r'^notafiscal_embarcando/$',
        views.NotafiscalEmbarcando.as_view(), name='notafiscal_embarcando'),

    url(r'^notafiscal_movimentadas/$',
        views.NotafiscalMovimentadas.as_view(),
        name='notafiscal_movimentadas'),

    url(r'^entrada_nf/_sem_xml/$',
        views.EntradaNfSemXml.as_view(), name='entr_nf_sem_xml'),

    url(r'^entrada_nf/lista/$',
        views.EntradaNfLista.as_view(), name='entr_nf_lista'),

]

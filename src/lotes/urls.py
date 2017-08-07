from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^posicao/$', views.Posicao.as_view(), name='posicao'),
    url(r'^posicao/(?P<lote>\d+)/$', views.Posicao.as_view(),
        name='posicao_lote'),
    url(r'^respons/$', views.respons, name='respons'),
    url(r'^op/$', views.Op.as_view(), name='op'),
    url(r'^op/(?P<op>\d+)/$', views.Op.as_view(), name='op_op'),
    url(r'^os/$', views.Os.as_view(), name='os'),
    url(r'^os/(?P<os>\d+)/$', views.Os.as_view(), name='os_os'),
    url(r'^por_alter/$', views.PorAlter.as_view(), name='por_alter'),
    url(r'^por_alter/(?P<periodo>\d+)/$', views.Os.as_view(),
        name='os_os_periodo'),

    # OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD OLD

    url(r'^posicao.old/$', views.posicaoOri, name='posicao.old'),
    url(r'^posicao.old/ajax/detalhes_lote/(\d{9})/$',
        views.detalhes_lote, name='detalhes_lote'),
]

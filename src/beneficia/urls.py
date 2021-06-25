from django.conf.urls import url

from . import views


app_name = 'beneficia'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ob/$', views.Ob.as_view(), name='ob'),
    url(r'^ob/(?P<ob>\d+)/$', views.Ob.as_view(), name='ob__get'),

    url(r'^busca_ob/$', views.BuscaOb.as_view(), name='busca_ob'),

    url(r'^ot/$', views.Ot.as_view(), name='ot'),
    url(r'^ot/(?P<ot>\d+)/$', views.Ot.as_view(), name='ot__get'),
]

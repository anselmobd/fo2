from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='cd'),
    url(r'^lote_local/$', views.LotelLocal.as_view(), name='cd_lote_local'),
    url(r'^estoque/$', views.Estoque.as_view(), name='cd_estoque'),
    url(r'^estoque/(?P<ordem>.)/(?P<filtro>.+)/$',
        views.Estoque.as_view(), name='cd_estoque_filtro'),
]

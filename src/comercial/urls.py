from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ficha_cliente/$', views.FichaCliente.as_view(),
        name='ficha_cliente'),
    url(r'^ficha_cliente/(?P<cnpj>\d+)/$', views.FichaCliente.as_view(),
        name='ficha_cliente__get'),
]

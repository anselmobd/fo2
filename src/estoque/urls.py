from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^por_deposito/$', views.PorDeposito.as_view(), name='por_deposito'),

    url(r'^valor_mp/$', views.ValorMp.as_view(), name='valor_mp'),
]

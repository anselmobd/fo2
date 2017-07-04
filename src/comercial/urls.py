from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ficha/$', views.FichaCliente.as_view(), name='ficha_cliente'),
]

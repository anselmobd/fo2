from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^data_saida/$', views.DataSaida.as_view(), name='data_saida'),
]

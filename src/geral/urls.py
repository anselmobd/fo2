from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^deposito/$', views.deposito, name='deposito'),
    url(r'^estagio/$', views.estagio, name='estagio'),
]

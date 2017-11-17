from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='comercial'),
    url(r'^ficha/$', views.FichaCliente.as_view(), name='ficha_cliente'),
    url(r'^ficha/(?P<cnpj>\d+)/$', views.FichaCliente.as_view(),
        name='ficha_cliente_cnpj'),
]

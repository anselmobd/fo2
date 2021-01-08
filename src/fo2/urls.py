import re

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from .admin import intr_adm_site
import fo2.views as views


admin.site.site_header = "Apoio ao ERP - Administração"
admin.site.site_title = "Apoio Admin"
admin.site.index_title = "Cadastros"


urlpatterns = [
    url(r'^$', views.index_view, name='index'),

    # url(r'^favicon\.ico$',
    #     RedirectView.as_view(url='/static/favicon.ico')),

    # url(r'^apoio_ao_erp/', views.ApoioAoErpView.as_view(),
    #     name='apoio_ao_erp'),

    # url(r'^intranet/', views.IntranetView.as_view(), name='intranet'),

    # Autenticação

    # url(r'^accounts/login/$',
    #     auth_views.login, {'template_name': 'login.html'}, name='login'),

    url(r'^encerrar/', auth_views.logout, {'next_page': '/'}, name='encerrar'),

    # Administração

    url(r'^rootadm/', admin.site.urls),

    url(r'^intradm/', intr_adm_site.urls),

    # Outras Apps

    url(r'^lotes/', include('lotes.urls', namespace='producao')),

    url(r'^produto/', include('produto.urls', namespace='produto')),

    url(r'^insumo/', include('insumo.urls', namespace='insumo')),

    url(r'^geral/', include('geral.urls', namespace='geral')),

    url(r'^contabil/', include('contabil.urls', namespace='contabil')),

    url(r'^comercial/', include('comercial.urls', namespace='comercial')),

    url(r'^logistica/', include('logistica.urls', namespace='logistica')),

    url(r'^rh/', include('rh.urls', namespace='rh')),

    url(r'^dp/', include('dp.urls', namespace='dp')),

    url(r'^cd/', include('cd.urls', namespace='cd')),

    url(r'^estoque/', include('estoque.urls', namespace='estoque')),

    url(r'^manutencao/', include('manutencao.urls', namespace='manutencao')),

    url(r'^email_signature/', include('email_signature.urls',
        namespace='email_signature')),

    url(r'^persona/', include('persona.urls', namespace='persona')),

    url(r'^base/', include('base.urls', namespace='base')),

    # Links para fora

    url(r'^systextil/', views.SystextilView.as_view(), name='systextil'),

    url(r'^ajax/router_ip_to_apoio_auth/',
        views.router_ip_to_apoio_auth, name='router_ip_to_apoio_auth'),

    # Links utilitários

    url(r'^myip/', views.myip_view, name='myip'),

    url(r'^meuip/', views.meuip_view, name='meuip'),

    url(r'^ack$', views.ack_view, name='ack'),

    # Acesso a teste.html para testes de html e css

    url(r'^t$', views.test_view, name='test'),

  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

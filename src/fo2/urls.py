import re

from django.urls import include, re_path
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
    re_path(r'^$', views.index_view, name='index'),

    # re_path(r'^favicon\.ico$',
    #     RedirectView.as_view(url='/static/favicon.ico')),

    # re_path(r'^apoio_ao_erp/', views.ApoioAoErpView.as_view(),
    #     name='apoio_ao_erp'),

    # re_path(r'^intranet/', views.IntranetView.as_view(), name='intranet'),

    # Autenticação

    # re_path(r'^accounts/login/$',
    #     auth_views.login, {'template_name': 'login.html'}, name='login'),

    re_path(r'^encerrar/', auth_views.LogoutView.as_view(next_page="/"), name='encerrar'),

    # Administração

    re_path(r'^rootadm/', admin.site.urls),

    re_path(r'^intradm/', intr_adm_site.urls),

    # Apps

    re_path(r'^base/', include('base.urls')),

    re_path(r'^beneficia/', include('beneficia.urls')),

    re_path(r'^cd/', include('cd.urls')),

    re_path(r'^comercial/', include('comercial.urls')),

    re_path(r'^contabil/', include('contabil.urls')),

    re_path(r'^dp/', include('dp.urls')),

    re_path(r'^email_signature/', include('email_signature.urls')),

    re_path(r'^estoque/', include('estoque.urls')),

    re_path(r'^geral/', include('geral.urls')),

    re_path(r'^insumo/', include('insumo.urls')),

    re_path(r'^itat/', include('itat.urls')),

    re_path(r'^logistica/', include('logistica.urls')),

    re_path(r'^lotes/', include('lotes.urls')),

    re_path(r'^manutencao/', include('manutencao.urls')),

    re_path(r'^persona/', include('persona.urls')),

    re_path(r'^produto/', include('produto.urls')),

    re_path(r'^rh/', include('rh.urls')),

    re_path(r'^servico/', include('servico.urls')),

    re_path(r'^systext/', include('systextil.urls')),

    re_path(r'^ti/', include('ti.urls')),

    # Links para fora

    re_path(r'^systextil/', views.SystextilView.as_view(), name='systextil'),

    re_path(r'^ajax/router_ip_to_apoio_auth/',
        views.router_ip_to_apoio_auth, name='router_ip_to_apoio_auth'),

    # Links utilitários

    re_path(r'^myip/', views.myip_view, name='myip'),

    re_path(r'^meuip/', views.meuip_view, name='meuip'),

    re_path(r'^ack$', views.ack_view, name='ack'),

    # Acesso a teste.html para testes de html e css

    re_path(r'^t$', views.test_view, name='test'),

  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

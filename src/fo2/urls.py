from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from .admin import intr_adm_site
from .views import index_view, test_view, IntranetView, myip_view, \
    SystextilView, ApoioAoErpView, ack_view


admin.site.site_header = "Apoio ao ERP - Administração"
admin.site.site_title = "Apoio Admin"
admin.site.index_title = "Cadastros"

urlpatterns = [
    url(r'^$', index_view, name='index'),

    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/favicon.ico')),

    url(r'^apoio_ao_erp/', ApoioAoErpView.as_view(), name='apoio_ao_erp'),

    url(r'^intranet/', IntranetView.as_view(), name='intranet'),

    # Autenticação

    url(r'^accounts/login/$',
        auth_views.login, {'template_name': 'login.html'}, name='login'),

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

    # Links para fora

    url(r'^systextil/', SystextilView.as_view(), name='systextil'),

    # Links utilitários

    url(r'^myip/', myip_view, name='myip'),

    url(r'^ack$', ack_view, name='ack'),

    # Acesso a teste.html para testes de html e css

    url(r'^t$', test_view, name='test'),

  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

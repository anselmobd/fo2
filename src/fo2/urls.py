from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from .admin import intr_adm_site
from .views import index_view, test_view, IntranetView, myip_view, \
    SystextilView, ApoioAoErpView


urlpatterns = [
    url(r'^$', index_view, name='index'),

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

    url(r'^geral/', include('geral.urls')),

    url(r'^contabil/', include('contabil.urls', namespace='contabil')),

    url(r'^comercial/', include('comercial.urls', namespace='comercial')),

    url(r'^logistica/', include('logistica.urls')),

    url(r'^rh/', include('rh.urls', namespace='rh')),

    url(r'^cd/', include('cd.urls')),

    # Links para fora

    url(r'^systextil/', SystextilView.as_view(), name='systextil'),

    # Links utilitários

    url(r'^myip/', myip_view, name='myip'),

    # Acesso a teste.html para testes de html e css

    url(r'^t$', test_view, name='test'),

  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

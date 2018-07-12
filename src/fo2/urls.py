"""fo2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from .admin import intr_adm_site
from .views import index_view, test_view, IntranetView, myip_view, \
    OficialSystextilView, ApoioAoErpView


urlpatterns = [
    url(r'^$', index_view, name='index'),
    url(r'^t$', test_view, name='test'),
    url(r'^apoio_ao_erp/', ApoioAoErpView.as_view(), name='apoio_ao_erp'),
    url(r'^intranet/', IntranetView.as_view(), name='intranet'),
    url(r'^accounts/login/$',
        auth_views.login, {'template_name': 'login.html'},
        name='login'),
    url(r'^encerrar/', auth_views.logout, {'next_page': '/'}, name='encerrar'),
    url(r'^myip/', myip_view, name='myip'),
    url(r'^oficial.systextil/', OficialSystextilView.as_view(),
        name='oficial_systextil'),
    # url(r'^', admin.site.urls),
    url(r'^rootadm/', admin.site.urls),
    url(r'^intradm/', intr_adm_site.urls),
    url(r'^lotes/', include('lotes.urls', namespace='producao')),
    url(r'^produto/', include('produto.urls')),
    url(r'^insumo/', include('insumo.urls', namespace='insumo')),
    url(r'^geral/', include('geral.urls')),
    url(r'^contabil/', include('contabil.urls')),
    url(r'^comercial/', include('comercial.urls')),
    url(r'^logistica/', include('logistica.urls')),
    url(r'^rh/', include('rh.urls')),
    url(r'^cd/', include('cd.urls')),
  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

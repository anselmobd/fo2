from django.conf.urls import url

from . import views


app_name = 'email_signature'
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^account/$', views.AccountListView.as_view(),
        name='account_list'),

    url(r'^account/add/$', views.AccountCreateView.as_view(),
        name='account_add'),

    url(r'^account/(?P<pk>[^/]+)/$', views.AccountUpdateView.as_view(),
        name='account_change'),

    url(r'^account/del/(?P<pk>[^/]+)/$',
        views.AccountDeleteView.as_view(),
        name='account_delete'),

    url(r'^show_template$', views.show_template, name='show_template'),

    url(r'^gerar_assinaturas$', views.GerarAssinaturas.as_view(),
        name='gerar_assinaturas'),
    url(r'^gerar_assinaturas/(?P<id>[^/]+)/$',
        views.GerarAssinaturas.as_view(), name='gerar_assinaturas'),

]

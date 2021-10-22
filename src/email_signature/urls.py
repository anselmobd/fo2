from django.urls import re_path

from . import views


app_name = 'email_signature'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path(r'^account/$', views.AccountListView.as_view(),
        name='account_list'),

    re_path(r'^account/add/$', views.AccountCreateView.as_view(),
        name='account_add'),

    re_path(r'^account/(?P<pk>[^/]+)/$', views.AccountUpdateView.as_view(),
        name='account_change'),

    re_path(r'^account/del/(?P<pk>[^/]+)/$',
        views.AccountDeleteView.as_view(),
        name='account_delete'),

    re_path(r'^show_template$',
        views.show_template,
        name='show_template'),
    re_path(r'^show_template/(?P<tipo>[^/]+)/$',
        views.show_template,
        name='show_template__get'),

    re_path(r'^ajax/gerar_assinatura/(?P<id>[^/]+)/$',
        views.ajax.gerar_assinatura,
        name='ajax_gerar_assinatura'),


]

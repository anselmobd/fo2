from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^accounts/$',
        views.Accounts.as_view(), name='accounts'),

    url(r'^emsign_account/$', views.AccountListView.as_view(),
        name='emsign_account_changelist'),

    url(r'^emsign_account/add/$', views.AccountCreateView.as_view(),
        name='emsign_account_add'),

    url(r'^emsign_account/(?P<pk>[^/]+)/$', views.AccountUpdateView.as_view(),
        name='emsign_account_change'),

    url(r'^emsign_account/del/(?P<pk>[^/]+)/$',
        views.AccountDeleteView.as_view(),
        name='emsign_account_delete'),

]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^account/$', views.AccountListView.as_view(),
        name='account_changelist'),

    url(r'^account/add/$', views.AccountCreateView.as_view(),
        name='account_add'),

    url(r'^account/(?P<pk>[^/]+)/$', views.AccountUpdateView.as_view(),
        name='account_change'),

    url(r'^account/del/(?P<pk>[^/]+)/$',
        views.AccountDeleteView.as_view(),
        name='account_delete'),

]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^accounts/$',
        views.Accounts.as_view(), name='accounts'),

]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ob/$', views.Ob.as_view(), name='ob'),
    url(r'^ob/(?P<ob>\d+)/$', views.Ob.as_view(), name='ob__get'),
]

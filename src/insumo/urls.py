from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^ref/$', views.Ref.as_view(), name='mp_ref'),
    url(r'^ref/(?P<item>[29]?\.?.{5})/$',
        views.Ref.as_view(), name='mp_ref_ref'),

]

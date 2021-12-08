from django.urls import re_path

from systextil.views import dba

urlpatterns = [

    re_path(r'^demorada/$', dba.Demorada.as_view(), name='demorada'),

    re_path(r'^travadora/$', dba.Travadora.as_view(), name='travadora'),

]

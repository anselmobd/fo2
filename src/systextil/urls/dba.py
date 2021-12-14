from django.urls import re_path

from systextil.views.dba import (
    demorada,
    travadora,
)


urlpatterns = [

    re_path(r'^demorada/$', demorada.Demorada.as_view(), name='demorada'),

    re_path(r'^travadora/$', travadora.Travadora.as_view(), name='travadora'),

]

from django.urls import re_path

from systextil.views import dba

app_name = 'dba'
urlpatterns = [

    re_path(r'^demorada/$', dba.demorada, name='demorada'),

]

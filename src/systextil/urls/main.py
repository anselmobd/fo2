from django.urls import include, re_path

from systextil.views import (
    index,
    sessions,
)


app_name = 'systextil'
urlpatterns = [
    re_path(r'^$', index.view, name='index'),

    re_path(r'^sessions/$', sessions.view, name='sessions'),

    re_path(r'^dba/', include('systextil.urls.dba'), name='dba'),
]

from django.urls import include, re_path

from systextil.views import (
    apoio_index,
    index,
    sessions,
)


app_name = 'systextil'
urlpatterns = [
    re_path(r'^$', index.view, name='index'),

    re_path(r'^apoio/$', apoio_index.view, name='apoio_index'),

    re_path(r'^dba/', include('systextil.urls.dba'), name='dba'),

    re_path(r'^sessions/$', sessions.view, name='sessions'),

    re_path(r'^table/', include('systextil.urls.table'), name='table'),

    re_path(r'^usuario/', include('systextil.urls.usuario'), name='usuario'),
]

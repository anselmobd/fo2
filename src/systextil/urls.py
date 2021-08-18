from django.urls import re_path

import systextil.views


app_name = 'systextil'
urlpatterns = [
    re_path(r'^$', systextil.views.index, name='index'),

    re_path(r'^sessions/$', systextil.views.sessions, name='sessions'),
]

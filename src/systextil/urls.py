from django.urls import re_path

import systextil.views.views


app_name = 'systextil'
urlpatterns = [
    re_path(r'^$', systextil.views.views.index, name='index'),

    re_path(r'^sessions/$', systextil.views.views.sessions, name='sessions'),
]

from django.urls import re_path

import ti.views


app_name = 'ti'
urlpatterns = [
    re_path(r'^$', ti.views.index, name='index'),
]

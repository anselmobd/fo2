from django.urls import re_path

from . import views


app_name = 'dp'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
]

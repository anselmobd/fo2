from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^aniversariantes/$',
        views.aniversariantes, name='aniversariantes_now'),
    url(r'^aniversariantes/(?P<ano>\d{4})/(?P<mes>\d{1,2})/?$',
        views.aniversariantes, name='aniversariantes'),

]

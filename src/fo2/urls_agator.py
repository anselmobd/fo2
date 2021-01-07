from fo2.urls import *


# para não acumular alterações, trabalha sempre em uma cópia nova
urlpatterns = urlpatterns.copy()

urlpatterns += [
    url(r'^$', views.index_agator_view, name='index'),

    url(r'^intranet/', views.IntranetAgatorView.as_view(), name='intranet'),
]

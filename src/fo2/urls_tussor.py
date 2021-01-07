from fo2.urls import *


# para não acumular alterações, trabalha sempre em uma cópia nova
urlpatterns = urlpatterns.copy()

urlpatterns += [
    url(r'^$', views.index_tussor_view, name='index'),

    url(r'^intranet/', views.IntranetTussorView.as_view(), name='intranet'),
]

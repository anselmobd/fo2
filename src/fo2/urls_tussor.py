from fo2.urls import *


# para não acumular alterações, trabalha sempre em uma cópia nova
urlpatterns = urlpatterns.copy()

urlpatterns += [
    url(r'^$', views.index_tussor_view, name='index'),

    url(r'^apoio_ao_erp/', views.ApoioAoErpView.as_view(),
        name='apoio_ao_erp'),

    url(r'^intranet/', views.IntranetTussorView.as_view(), name='intranet'),
]

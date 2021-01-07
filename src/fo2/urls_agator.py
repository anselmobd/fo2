from fo2.urls import *


# para não acumular alterações, trabalha sempre em uma cópia nova
urlpatterns = urlpatterns.copy()

urlpatterns.append(
    url(r'^$', views.index_agator_view, name='index'),
)

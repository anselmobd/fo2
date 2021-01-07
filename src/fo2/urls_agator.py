from fo2.urls import *


urlpatterns = clean_urlpatterns(urlpatterns, '^$')

urlpatterns.append(
    url(r'^$', views.index_agator_view, name='index'),
)

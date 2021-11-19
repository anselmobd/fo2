from pprint import pprint

from django.contrib.auth import views as auth_views
from django.urls import re_path
from django.views.generic import RedirectView

import fo2.views as views
from fo2.urls import urlpatterns


# para não acumular alterações, trabalha sempre em uma cópia nova
urlpatterns = urlpatterns.copy()

urlpatterns += [

    re_path(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/favicon_agator.ico')),

    re_path(r'^apoio_ao_erp/', views.ApoioAoErpAgatorView.as_view(),
        name='apoio_ao_erp'),

    re_path(r'^intranet/', views.IntranetAgatorView.as_view(), name='intranet'),

    # Autenticação

    re_path(r'^accounts/login/$',
        auth_views.LoginView.as_view(template_name="login_agator.html"), name='login'),

]

from fo2.urls import *


# para não acumular alterações, trabalha sempre em uma cópia nova
urlpatterns = urlpatterns.copy()

urlpatterns += [

    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/favicon_agator.ico')),

    url(r'^apoio_ao_erp/', views.ApoioAoErpAgatorView.as_view(),
        name='apoio_ao_erp'),

    url(r'^intranet/', views.IntranetAgatorView.as_view(), name='intranet'),

    # Autenticação

    url(r'^accounts/login/$',
        auth_views.LoginView.as_view(template_name="login_agator.html"), name='login'),

]

from django.urls import re_path
from systextil.views import apoio_index

from systextil.views.usuario import (
    zera_senha,
)


urlpatterns = [

    re_path(r'^zera_senha/$', zera_senha.ZeraSenha.as_view(), name='zera_senha'),

]

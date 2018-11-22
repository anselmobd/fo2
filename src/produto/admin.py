from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import GtinRange, Produto
from .forms import ProdutoForm


class GtinRangeAdmin(admin.ModelAdmin):
    search_fields = ['codigo']
    ordering = ['ordem']
    fields = ['ordem', 'pais', 'codigo']


class ProdutoAdmin(admin.ModelAdmin):
    form = ProdutoForm
    search_fields = ['referencia']
    ordering = ['referencia']


intr_adm_site.register(GtinRange, GtinRangeAdmin)
intr_adm_site.register(Produto, ProdutoAdmin)

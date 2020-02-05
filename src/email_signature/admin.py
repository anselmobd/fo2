from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import Layout


class LayoutAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'template', 'habilitado']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome', 'slug', 'template', 'habilitado']
    readonly_fields = ['slug']


intr_adm_site.register(Layout, LayoutAdmin)

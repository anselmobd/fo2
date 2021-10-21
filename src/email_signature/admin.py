from django.contrib import admin

from fo2.admin import intr_adm_site

import email_signature.models


@admin.register(email_signature.models.Account, site=intr_adm_site)
class AccountAdmin(admin.ModelAdmin):
    ordering = ['email']
    readonly_fields = ['create_at', 'update_at']


@admin.register(email_signature.models.Layout, site=intr_adm_site)
class LayoutAdmin(admin.ModelAdmin):
    list_display = ['slug', 'tipo', 'nome', 'template', 'habilitado']
    search_fields = ['tipo', 'nome', 'slug', 'template']
    ordering = ['slug']
    fields = ['tipo', 'nome', 'slug', 'template', 'habilitado']
    readonly_fields = ['slug']

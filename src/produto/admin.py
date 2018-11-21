from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import GtinRange


class GtinRangeAdmin(admin.ModelAdmin):
    search_fields = ['codigo']
    ordering = ['ordem']
    fields = ['ordem', 'codigo']


intr_adm_site.register(GtinRange, GtinRangeAdmin)

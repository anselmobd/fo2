from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import RecordTracking


class RecordTrackingAdmin(admin.ModelAdmin):
    list_display = ['time', 'table', 'record_id', 'iud', 'log', 'user']
    search_fields = ['table', 'log', 'user']
    ordering = ['time', 'table', 'record_id']
    fields = ['time', 'table', 'record_id', 'iud', 'log', 'user']
    readonly_fields = ['time', 'table', 'record_id', 'iud', 'log', 'user']


intr_adm_site.register(RecordTracking, RecordTrackingAdmin)

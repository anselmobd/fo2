from django.contrib import admin

from fo2.admin import intr_adm_site
from .models import RecordTracking


class RecordTrackingAdmin(admin.ModelAdmin):
    list_display = ['table', 'record_id', 'iud', 'log']
    search_fields = ['table', 'log']
    ordering = ['record_id']
    fields = ['table', 'record_id', 'iud', 'log']
    readonly_fields = ['table', 'record_id', 'iud', 'log']


intr_adm_site.register(RecordTracking, RecordTrackingAdmin)

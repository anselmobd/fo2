from django.contrib import admin
from django.contrib.admin.models import LogEntry

from django.contrib.admin import AdminSite


class IntrAdmSite(AdminSite):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.site_header = 'Apoio ao ERP (Tussor) - Cadastros'
        self.site_title = 'Fo2 - Apoio ao ERP (Tussor) - Cadastros'
        self.index_title = 'Cadastros'
        self.enable_nav_sidebar = False


intr_adm_site = IntrAdmSite(name='intradm')


# Alter root admin site to show LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    search_fields = ('object_repr', 'object_id')
    list_filter = ('action_time', 'content_type',)
    list_display = ('action_time', 'user', 'content_type', 'tipo',
                    'object_repr')
    fields = ('action_time', 'user', 'content_type', 'object_id',
              'object_repr', 'action_flag', 'change_message', )
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id',
                       'object_repr', 'action_flag', 'tipo', 'change_message',)

    def tipo(self, obj):
        if obj.is_addition():
            return u"Adicionado"
        elif obj.is_change():
            return u"Modificado"
        elif obj.is_deletion():
            return u"Deletado"


admin.site.register(LogEntry, LogEntryAdmin)

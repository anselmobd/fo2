from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoMaquina, UnidadeTempo


class TipoMaquinaAdmin(admin.ModelAdmin):
    fields = ['nome', 'slug', 'descricao']
    readonly_fields = ['slug']


class UnidadeTempoAdmin(admin.ModelAdmin):
    fields = ['codigo', 'nome']
    readonly_fields = ['codigo', 'nome']


intr_adm_site.register(TipoMaquina, TipoMaquinaAdmin)
intr_adm_site.register(UnidadeTempo, UnidadeTempoAdmin)

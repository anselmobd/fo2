from django.contrib import admin

from fo2.admin import intr_adm_site

from .models import TipoMaquina, UnidadeTempo, Maquina


class TipoMaquinaAdmin(admin.ModelAdmin):
    fields = ['nome', 'slug', 'descricao']
    readonly_fields = ['slug']


class UnidadeTempoAdmin(admin.ModelAdmin):
    fields = ['codigo', 'nome']
    readonly_fields = ['codigo', 'nome']


class MaquinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    fields = ['tipo_maquina', 'nome', 'slug', 'descricao']
    readonly_fields = ['slug']


intr_adm_site.register(TipoMaquina, TipoMaquinaAdmin)
intr_adm_site.register(UnidadeTempo, UnidadeTempoAdmin)
intr_adm_site.register(Maquina, MaquinaAdmin)

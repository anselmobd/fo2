from django.contrib import admin

from fo2 import settings
from fo2.admin import intr_adm_site
from .models import Impresso, ImpressoraTermica, ModeloTermica, UsuarioImpresso
from .forms import ModeloTermicaForm


class ImpressoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome']


class ImpressoraTermicaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    ordering = ['nome']
    fields = ['nome']


class ModeloTermicaAdmin(admin.ModelAdmin):
    form = ModeloTermicaForm
    list_display = ['codigo', 'nome']
    search_fields = ['codigo', 'nome']
    ordering = ['codigo']
    fields = ['codigo', 'nome', 'modelo', 'receita']

    class Media:
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        js = [static_url+'/admin/lotes/modeloTermica.js', ]


class ImpressoInline(admin.TabularInline):
    model = Impresso


class ImpressoraTermicaInline(admin.TabularInline):
    model = ImpressoraTermica


class ModeloTermicaInline(admin.TabularInline):
    model = ModeloTermica


class UsuarioImpressoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'impresso',
                    'impressora_termica', 'modelo']
    ordering = ['usuario__username', 'impresso__nome',
                'impressora_termica__nome', 'modelo__codigo']
    search_fields = ['usuario__username', 'impresso__nome',
                     'impressora_termica__nome', 'modelo__codigo']
    fields = ['usuario', 'impresso',
              'impressora_termica', 'modelo']


intr_adm_site.register(Impresso, ImpressoAdmin)
intr_adm_site.register(ImpressoraTermica, ImpressoraTermicaAdmin)
intr_adm_site.register(ModeloTermica, ModeloTermicaAdmin)
intr_adm_site.register(UsuarioImpresso, UsuarioImpressoAdmin)

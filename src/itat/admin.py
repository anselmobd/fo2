from django.contrib import admin

from fo2.admin import intr_adm_site

import itat.forms
import itat.models


@admin.register(itat.models.Company, site=intr_adm_site)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.Location, site=intr_adm_site)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['slug', 'company', 'name']
    search_fields = ['slug', 'company__name', 'company__slug', 'name']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.OSType, site=intr_adm_site)
class OSTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.OS, site=intr_adm_site)
class OSAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'version', 'bits', 'slug']
    search_fields = ['slug', 'type__name',
                     'type__slug', 'name', 'version', 'bits']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.EquipmentType, site=intr_adm_site)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.Equipment, site=intr_adm_site)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['slug', 'type', 'name', 'description',
                    'application', 'users', 'primary_ip']
    search_fields = ['slug', 'type__name', 'type__slug', 'name',
                     'description', 'application', 'users', 'primary_ip']
    ordering = ['slug']
    readonly_fields = ['slug']
    fields = (
        'type',
        ('name', 'slug'),
        'description',
        'use',
        'users',
        'primary_ip',
    )


@admin.register(itat.models.InterfaceType, site=intr_adm_site)
class InterfaceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'slug']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.Interface, site=intr_adm_site)
class InterfaceAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'type', 'name',
                    'slug', 'mac_adress', 'fixed_ip']
    search_fields = ['equipment__name', 'interface__name', 'type__name',
                     'type__slug', 'name', 'slug', 'mac_adress', 'fixed_ip']
    ordering = ['type', 'slug']
    readonly_fields = ['slug']


@admin.register(itat.models.DhcpConfig, site=intr_adm_site)
class DhcpConfigAdmin(admin.ModelAdmin):
    form = itat.forms.DhcpConfigForm
    list_display = ['name', 'slug', 'primary_equipment', 'secondary_equipment']
    search_fields = ['name', 'slug',
                     'primary_equipment__name', 'secondary_equipment__name']
    ordering = ['slug']
    readonly_fields = ['slug']


@admin.register(itat.models.Share, site=intr_adm_site)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment', 'path', 'read_only']
    search_fields = ['name', 'equipment', 'path', 'read_only']
    ordering = ['name']

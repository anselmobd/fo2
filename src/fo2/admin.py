from django.contrib.admin import AdminSite


class IntrAdmSite(AdminSite):
    site_header = 'Intranet - Tussor - Administração'


intr_adm_site = IntrAdmSite(name='intradm')

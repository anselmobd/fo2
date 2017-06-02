from django.contrib.admin import AdminSite
# from .models import MyModel

# from django.contrib.auth.models import User, Group


class IntrAdmSite(AdminSite):
    site_header = 'Intranet - Tussor - Administração'


intr_adm_site = IntrAdmSite(name='intradm')
# admin_site.register(MyModel)

# admin_site.register(User)
# admin_site.register(Group)

from django.contrib.admin import AdminSite
# from .models import MyModel

from django.contrib.auth.models import User, Group



class MyAdminSite(AdminSite):
    site_header = 'Intranet - Tussor - Administração'


admin_site = MyAdminSite(name='myadmin')
# admin_site.register(MyModel)
admin_site.register(User)
admin_site.register(Group)

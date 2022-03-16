from pprint import pprint

from django.db import models


class CdPermissions(models.Model):

    class Meta:
        verbose_name = 'Permissões do CD'
        managed = False
        permissions = (
            ("can_admin_pallet", "Pode administrar paletes"),
        )

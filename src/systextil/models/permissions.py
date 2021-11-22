from django.db import models


class SystextilPermissions(models.Model):
    class Meta:
        managed = False
        permissions = (
            ("can_be_dba", "Can be DBA"),
        )

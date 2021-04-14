from django.db import models
from django.utils import timezone


class CsrfToken(models.Model):
    at = models.DateTimeField(
        null=True, blank=True,
    )
    token = models.CharField(
        max_length=128,
    )

    class Meta:
        db_table = 'o2_csrf_token'
        verbose_name = 'CSRF Token utilizado'
        verbose_name_plural = 'CSRF Tokens utilizados'

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.id:
            self.create_at = now
        super(CsrfToken, self).save(*args, **kwargs)

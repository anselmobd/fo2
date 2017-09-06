from django.db.models.signals import post_init, post_save

from fo2.signals import post_init_tracking, post_save_tracking
from .models import NotaFiscal


post_init.connect(post_init_tracking, sender=NotaFiscal)

post_save.connect(post_save_tracking, sender=NotaFiscal)

from django.db.models.signals import post_init, post_save, post_delete

from geral.signals import post_init_tracking, post_save_tracking, post_delete_tracking
from .models import NotaFiscal, NfEntrada


post_init.connect(post_init_tracking, sender=NotaFiscal)
post_init.connect(post_init_tracking, sender=NfEntrada)

post_save.connect(post_save_tracking, sender=NotaFiscal)
post_save.connect(post_save_tracking, sender=NfEntrada)

post_delete.connect(post_delete_tracking, sender=NfEntrada)

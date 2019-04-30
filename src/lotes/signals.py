from django.db.models.signals import post_init, post_save, post_delete

from fo2.signals import \
    post_init_tracking, post_save_tracking, post_delete_tracking
from .models import ModeloTermica, ImpressoraTermica, Lote, \
    SolicitaLote, SolicitaLoteQtd


post_init.connect(post_init_tracking, sender=ModeloTermica)
post_init.connect(post_init_tracking, sender=ImpressoraTermica)
post_init.connect(post_init_tracking, sender=Lote)
post_init.connect(post_init_tracking, sender=SolicitaLote)
post_init.connect(post_init_tracking, sender=SolicitaLoteQtd)

post_save.connect(post_save_tracking, sender=ModeloTermica)
post_save.connect(post_save_tracking, sender=ImpressoraTermica)
post_save.connect(post_save_tracking, sender=Lote)
post_save.connect(post_save_tracking, sender=SolicitaLote)
post_save.connect(post_save_tracking, sender=SolicitaLoteQtd)

post_delete.connect(post_delete_tracking, sender=ModeloTermica)
post_delete.connect(post_delete_tracking, sender=ImpressoraTermica)
post_delete.connect(post_delete_tracking, sender=Lote)
post_delete.connect(post_delete_tracking, sender=SolicitaLote)
post_delete.connect(post_delete_tracking, sender=SolicitaLoteQtd)

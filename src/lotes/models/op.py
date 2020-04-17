from django.db import models


class Op(models.Model):
    op = models.IntegerField(
        verbose_name='OP')
    pedido = models.IntegerField()
    varejo = models.BooleanField(default=False)
    cancelada = models.BooleanField(default=False)
    deposito = models.IntegerField(default=-1)

    class Meta:
        db_table = "fo2_prod_op"
        permissions = (("can_repair_seq_op", "Can repair sequence OP"),
                       )

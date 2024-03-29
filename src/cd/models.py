from pprint import pprint

from django.db import models


class CdPermissions(models.Model):

    class Meta:
        verbose_name = 'Permissões do CD'
        managed = False
        permissions = (
            ("can_admin_pallet", "Pode administrar paletes"),
            ("can_view_grades_estoque", "Pode visualizar grades do estoque"),
            ("can_del_lote_de_palete", "Pode retirar lote de palete"),
            (
                "pode_finalizar_empenho_op_finalizada",
                "Pode finalizar empenho de OP finalizada",
            ),
            ("imprime_etq_palete", "Imprime etiqueta de palete"),
        )

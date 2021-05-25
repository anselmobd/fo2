from django.db import models


class LotesPermissions(models.Model):

    class Meta:
        managed = False
        permissions = (
            ("can_edit_estagio_direito", "Can edit direitos a estágios"),
            ("can_print__solicitacao_parciais",
             "Pode imprimir etiquetas de solicitações parciais"),
            ("can_reabrir_solicitacao_completada",
             "Pode reabrir solicitação marada como completa"),
            ("libera_coleta_de_solicitacao",
             "Libera coleta de solicitação"),
            ("manutencao-de-regra-de-lote-por-caixa",
             "Manutenção de regra de lote por caixa"),
        )

import django_tables2 as tables

import lotes.models as models


class CustomTable(tables.Table):

    class Meta:
        order_by_field = 'ordem'
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}


class ImpressoraTermicaTable(CustomTable):

    class Meta(CustomTable.Meta):
        model = models.ImpressoraTermica
        fields = ['nome']
        order_by = 'nome'

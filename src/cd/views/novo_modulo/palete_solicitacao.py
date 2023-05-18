from pprint import pprint

from django.contrib.postgres.aggregates import StringAgg

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.dictlist import queryset2dictlist, dictlist_agg
from utils.functions.models.row_field import PrepRows
from utils.table_defs import TableDefsHpS

from lotes.functions.varias import modelo_de_ref

from produto.forms import ModeloForm
from produto import models


__all__ = ['PaleteSolicitacaoView']


class PaleteSolicitacaoView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(PaleteSolicitacaoView, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm
        self.template_name = 'cd/novo_modulo/palete_solicitacao.html'
        self.title_name = 'Palete/Solicitacao'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        modelo = int(self.modelo)

        referencias = models.Produto.objects.filter(referencia__contains=str(modelo)).values(
            'referencia',
        ).order_by('referencia')

        ref_list = []
        for referencia in referencias:
            if modelo_de_ref(referencia['referencia']) == modelo:
                ref_list.append(referencia['referencia'])

        produtos = models.Produto.objects.filter(
            referencia__in=ref_list,
        ).values(
            'nivel',
            'referencia',
            'descricao',
            'produtotamanho__tamanho__nome',
            'ativo',
            'cor_no_tag',
        ).annotate(
            cores=StringAgg('produtocor__cor', delimiter=', ', distinct=True),
        ).order_by('nivel', 'referencia', 'produtotamanho__tamanho__ordem')

        refs = dictlist_agg(
            produtos,
            'produtotamanho__tamanho__nome',
            agg_key='tamanhos'
        )

        PrepRows(
            refs,
        ).a_blank(
            'referencia', 'produto:ref__get'
        ).sn(
            ['ativo', 'cor_no_tag']
        ).process()

        self.context['refs'] = TableDefsHpS({
            'nivel': 'Nível',
            'referencia': "Ref.",
            'descricao': "Descrição",
            'tamanhos': "Tamanhos",
            'cores': "Cores",
            'ativo': 'Ativo',
            'cor_no_tag': 'Cor no tag?',
        }).hfs_dict()
        self.context['refs'].update({
            'title': 'Referências',
            'data': refs,
            'thclass': 'sticky',
            'empty': "Nenhuma encontrada",
        })

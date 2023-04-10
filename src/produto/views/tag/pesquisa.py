from pprint import pprint

from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.models.dictlist import queryset_to_dictlist_lower
from utils.functions.models.row_field import PrepRows
from utils.table_defs import TableDefsHpS

from produto.forms import ModeloForm
from produto import models


__all__ = ['TagPesquisaView']


class TagPesquisaView(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(TagPesquisaView, self).__init__(*args, **kwargs)
        self.Form_class = ModeloForm
        self.template_name = 'produto/tag/pesquisa.html'
        self.title_name = 'TAG - Pesquisa'
        self.cleaned_data2self = True
        self.get_args2context = True
        self.form_class_has_initial = True

    def mount_context(self):
        modelo = int(self.modelo)

        produtos = models.Produto.objects.all().order_by('nivel', 'referencia')

        filter = (lambda r: r.modelo == modelo) if modelo else None
        refs = queryset_to_dictlist_lower(produtos, filter)

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
            'ativo': 'Ativo',
            'cor_no_tag': 'Cor no tag?',
        }).hfs_dict()
        self.context['refs'].update({
            'title': 'Referências',
            'data': refs,
            'thclass': 'sticky',
            'empty': "Nenhuma encontrada",
        })

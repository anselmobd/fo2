from base.forms import O2BaseForm, O2FieldOrdemForm


class OrdensForm(
        O2BaseForm,
        O2FieldOrdemForm):

    class Meta:
        autofocus_field = 'ordem'


class OrdemForm(
        O2BaseForm,
        O2FieldOrdemForm):

    class Meta:
        autofocus_field = 'ordem'

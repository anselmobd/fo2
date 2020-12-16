from pprint import pprint

from django import forms


class RoloForm(forms.Form):
    rolo = forms.CharField(
        label='Rolo', max_length=7, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

    choices_sit = [
        ('', '(não filtra)'),
        ('0', '0-Em produção'),
        ('1', '1-Em estoque'),
        ('2', '2-Faturado ou fora do estoque'),
        ('3', '3-Relacionado a pedido'),
        ('4', '4-Em trânsito'),
        ('5', '5-Coletado'),
        ('7', '7-Relacionado a ordem de serviço'),
        ('8', '8-Rolo com nota emitida em processo de cancelamento'),
    ]
    sit = forms.ChoiceField(
        label='Situação', choices=choices_sit, initial='', required=False)

    ref = forms.CharField(
        label='Referência (nível 2)', max_length=5, required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'size': 5}))

    cor = forms.CharField(
        label='Cor', max_length=6, required=False,
        widget=forms.TextInput(
            attrs={'type': 'string', 'size': 6}))

    op = forms.CharField(
        label='OP', max_length=7, required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    choices_est_res = [
        ('', '(não filtra)'),
        ('S', 'Reservado'),
        ('N', 'Não reservado'),
    ]
    est_res = forms.ChoiceField(
        label='Estado da reserva', choices=choices_est_res, initial='', required=False)

    choices_est_aloc = [
        ('', '(não filtra)'),
        ('S', 'Alocado'),
        ('N', 'Não alocado'),
    ]
    est_aloc = forms.ChoiceField(
        label='Estado da alocação', choices=choices_est_aloc, initial='', required=False)

    choices_est_conf = [
        ('', '(não filtra)'),
        ('S', 'Confirmado'),
        ('N', 'Não confirmado'),
    ]
    est_conf = forms.ChoiceField(
        label='Estado da confirmação', choices=choices_est_conf, initial='', required=False)

    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor

    def clean(self):
        clean_form = super(RoloForm, self).clean()

        if not any(
            clean_form.get(x, '')
            for x in (
                'rolo',
                'sit',
                'ref',
                'cor',
                'op',
                'est_res',
                'est_aloc',
                'est_conf',
            )
        ):
            list_msg = ['Ao menos um destes campos deve ser preenchido']
            self._errors['rolo'] = self.error_class(list_msg)

        return clean_form

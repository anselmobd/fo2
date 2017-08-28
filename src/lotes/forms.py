from django import forms


class LoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class OpForm(forms.Form):
    op = forms.CharField(
        label='OP',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class OsForm(forms.Form):
    os = forms.CharField(
        label='OS',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class AnPeriodoAlterForm(forms.Form):
    periodo_de = forms.CharField(
        label='Período: De',
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    periodo_ate = forms.CharField(
        label='Até', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))

    def clean_periodo(self, periodo):
        try:
            i_periodo = int(float(periodo))
            if i_periodo < 0:
                periodo = None
        except ValueError:
            periodo = None
        return periodo

    def clean_periodo_de(self):
        return self.clean_periodo(self.cleaned_data['periodo_de'])

    def clean_periodo_ate(self):
        return self.clean_periodo(self.cleaned_data['periodo_ate'])


class AnDtCorteAlterForm(forms.Form):
    data_de = forms.DateField(
        label='Data do Corte/Gargalo: De',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Até', required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))

    # alternativa = forms.CharField(
    #     label='Alternativa', required=False,
    #     widget=forms.TextInput(attrs={'type': 'number'}))
    # roteiro = forms.CharField(
    #     label='Roteiro', required=False,
    #     widget=forms.TextInput(attrs={'type': 'number'}))
    # tipo = forms.CharField(
    #     label='Tipo (MD, PG, PA)', required=False, widget=forms.TextInput)
    #
    # def clean_tipo(self):
    #     tipo = self.cleaned_data['tipo'].upper()
    #     if tipo not in ('MD', 'PG', 'PA'):
    #         tipo = ''
    #     return tipo


class ResponsPorEstagioForm(forms.Form):
    estagio = forms.CharField(
        label='Estágio', max_length=2, required=False,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    usuario = forms.CharField(
        label='Usuário', max_length=20, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))
    CHOICES = [('e', 'Por estágio'),
               ('u', 'Por usuário')]
    ordem = forms.ChoiceField(
        choices=CHOICES, initial='e', widget=forms.RadioSelect())

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario'].upper()
        data = self.data.copy()
        data['usuario'] = usuario
        self.data = data
        return usuario

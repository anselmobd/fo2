from django import forms


class LoteForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', min_length=2, max_length=4,
        help_text='(Informe endereço, para posicionar o lote no CD, '
                  'ou o "SAI" para tirar o lote do CD)',
        widget=forms.TextInput())
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))
    identificado = forms.CharField(
        label='identificado', required=False,
        widget=forms.HiddenInput())

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if endereco != "SAI":
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "Deve iniciar com uma letra.")
            if not endereco[1:].isdigit():
                raise forms.ValidationError(
                    "Depois da letra inicial deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco


class TrocaLocalForm(forms.Form):
    endereco_de = forms.CharField(
        label='Endereço antigo', min_length=2, max_length=4,
        widget=forms.TextInput())
    endereco_para = forms.CharField(
        label='Endereço novo', min_length=2, max_length=4,
        widget=forms.TextInput())

    def limpa_endereco(self, campo):
        endereco = self.cleaned_data[campo].upper()
        if not endereco[0].isalpha():
            raise forms.ValidationError(
                "Deve iniciar com uma letra.")
        if not endereco[1:].isdigit():
            raise forms.ValidationError(
                "Depois da letra inicial deve ter apenas números.")
        data = self.data.copy()
        data[campo] = endereco
        self.data = data
        return endereco

    def clean_endereco_de(self):
        return self.limpa_endereco('endereco_de')

    def clean_endereco_para(self):
        return self.limpa_endereco('endereco_para')

    def clean(self):
        cleaned_data = super(TrocaLocalForm, self).clean()
        if cleaned_data['endereco_de'] == cleaned_data['endereco_para']:
            raise forms.ValidationError(
                "Os endereços devem ser diferentes.")
        return cleaned_data


class EstoqueForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', required=False, min_length=2, max_length=4,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    lote = forms.CharField(
        label='Lote', required=False, min_length=9, max_length=9,
        widget=forms.TextInput(attrs={'type': 'number'}))
    op = forms.CharField(
        label='OP', required=False,
        widget=forms.TextInput(attrs={'type': 'number'}))
    ref = forms.CharField(
        label='Referência', required=False, min_length=5, max_length=5,
        widget=forms.TextInput(attrs={'type': 'string'}))
    tam = forms.CharField(
        label='Tamanho', required=False, min_length=1, max_length=3,
        widget=forms.TextInput(attrs={'type': 'string'}))
    cor = forms.CharField(
        label='Cor', required=False, min_length=1, max_length=6,
        widget=forms.TextInput(attrs={'type': 'string'}))
    data_de = forms.DateField(
        label='Data inicial', required=False,
        help_text='(Data de bipagem)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    data_ate = forms.DateField(
        label='Data final', required=False,
        help_text='(Se não informar, assume igual a inicial.)',
        widget=forms.DateInput(attrs={'type': 'date'}))
    CHOICES = [('B', 'Hora de bipagem'),
               ('O', 'OP Referência Cor Tamanho Endereço Lote'),
               ('R', 'Referência Cor Tamanho Endereço OP Lote'),
               ('E', 'Endereço OP Referência Cor Tamanho Lote')]
    ordem = forms.ChoiceField(
        label='Ordenação', choices=CHOICES, initial='B')
    page = forms.IntegerField(
        required=False, widget=forms.HiddenInput())

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if endereco:
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "Deve iniciar com uma letra.")
            if not endereco[1:].isdigit():
                raise forms.ValidationError(
                    "Depois da letra inicial deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref

    def clean_tam(self):
        tam = self.cleaned_data['tam'].upper()
        data = self.data.copy()
        data['tam'] = tam
        self.data = data
        return tam

    def clean_cor(self):
        cor = self.cleaned_data['cor'].upper()
        if cor:
            cor = cor.zfill(6)
        data = self.data.copy()
        data['cor'] = cor
        self.data = data
        return cor


class ConfereForm(forms.Form):
    endereco = forms.CharField(
        label='Endereço', required=False, min_length=1, max_length=4,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    def clean_endereco(self):
        endereco = self.cleaned_data['endereco'].upper()
        if endereco:
            if not endereco[0].isalpha():
                raise forms.ValidationError(
                    "Deve iniciar com uma letra.")
            if len(endereco) > 1:
                if not endereco[1:].isdigit():
                    raise forms.ValidationError(
                        "Depois da letra inicial deve ter apenas números.")
        data = self.data.copy()
        data['endereco'] = endereco
        self.data = data
        return endereco


class SolicitacaoForm(forms.Form):
    codigo = forms.CharField(
        label='Código', max_length=20, min_length=1,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    descricao = forms.CharField(
        label='Descrição', required=False,
        widget=forms.TextInput(attrs={'size': 60}))
    ativa = forms.BooleanField(
        label='Ativa para o usuário', required=False)


class AskLoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class AskReferenciaForm(forms.Form):
    ref = forms.CharField(
        label='Filtro', required=False, max_length=5,
        help_text='(referência, com 5 caracteres, '
                  'ou parte numérica da referência ou vazio)',
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_ref(self):
        ref = self.cleaned_data['ref'].upper()
        data = self.data.copy()
        data['ref'] = ref
        self.data = data
        return ref


class HistoricoForm(forms.Form):
    op = forms.CharField(
        label='OP', required=True,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))


class ALoteForm(forms.Form):
    lote = forms.CharField(
        label='Lote', max_length=9, min_length=9,
        widget=forms.TextInput(attrs={'type': 'number',
                               'autofocus': 'autofocus'}))

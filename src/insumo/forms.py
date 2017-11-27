from django import forms


class RefForm(forms.Form):
    item = forms.CharField(
        label='Referência', max_length=7, min_length=5,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))

    def clean_item(self):
        item = self.cleaned_data['item'].upper()
        data = self.data.copy()
        data['item'] = item
        self.data = data
        return item


class RolosBipadosForm(forms.Form):
    ref = forms.CharField(
        label='Referência', max_length=5, required=False,
        widget=forms.TextInput(attrs={'type': 'string',
                               'autofocus': 'autofocus'}))
    cor = forms.CharField(
        label='Cor', max_length=6, required=False,
        widget=forms.TextInput(attrs={'type': 'string'}))

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

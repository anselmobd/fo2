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

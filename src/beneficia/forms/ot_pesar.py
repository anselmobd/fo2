from django import forms

from o2.forms.widget_attrs import FormWidgetAttrs
from utils.functions.date import today_ymd


class OtPesarForm(forms.Form):
    a = FormWidgetAttrs()

    periodo = forms.CharField(
        label='Período',
        required=False,
        widget=forms.TextInput(
            attrs={
                **a.autofocus,
                **a.number,
                'size': 4,
            }
        )
    )

    data = forms.DateField(
        label="Data dentro do período",
        required=False,
        initial=today_ymd,
        widget=forms.DateInput(
            attrs={
                **a.date,
            }
        ),
    )

    CHOICES = [
        ('s', "Somente OTs com algum insumo sem pesagem"),
        ('t', "Todas as OTs com insumos que devem ser pesados"),
    ]
    selecao = forms.ChoiceField(
        label="Seleção",
        choices=CHOICES,
        initial='s',
    )


    def clean(self):
        clean_ef = super(OtPesarForm, self).clean()

        if not any(
            clean_ef.get(x, '')
            for x in (
                'periodo',
                'data',
            )
        ):
            list_msg = ['Ao menos um destes campos deve ser preenchido']
            self._errors['periodo'] = self.error_class(list_msg)
            self._errors['data'] = self.error_class(list_msg)

        return clean_ef

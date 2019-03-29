from django.shortcuts import render
from django.views import View


class O2BaseView(View):

    def start(self, request, kwargs):
        self.request = request
        self.kwargs = kwargs
        self.context = {'titulo': self.title_name}

    def end(self):
        self.context['form'] = self.form
        return render(self.request, self.template_name, self.context)

    def get_arg(self, field):
        return self.kwargs[field] if field in self.kwargs else None

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:
            self.form.data[field] = value

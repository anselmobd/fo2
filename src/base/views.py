from django.shortcuts import render
from django.views import View


class O2BaseCustomView(View):

    def __init__(self):
        self.get_args = []

    def init_self(self, request, kwargs):
        self.request = request
        self.kwargs = kwargs
        self.context = {'titulo': self.title_name}

    def get_arg(self, field):
        return self.kwargs[field] if field in self.kwargs else None

    def my_render(self):
        return render(self.request, self.template_name, self.context)


class O2BaseGetPostView(O2BaseCustomView):

    def render_mount(self):
        if self.form.is_valid():
            self.mount_context()
        self.context['form'] = self.form
        return self.my_render()

    def set_form_arg(self, field):
        value = self.get_arg(field)
        if value is not None:
            self.form.data[field] = value

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)

        for arg in self.get_args:
            if self.get_arg(arg) is not None:
                return self.post(request, *args, **kwargs)

        self.form = self.Form_class()
        return self.render_mount()

    def post(self, request, *args, **kwargs):
        self.init_self(request, kwargs)
        self.form = self.Form_class(self.request.POST)

        for arg in self.get_args:
            self.set_form_arg(arg)

        return self.render_mount()


class O2BaseGetView(O2BaseCustomView):

    def render_mount(self):
        self.mount_context()
        return self.my_render()

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)

        return self.render_mount()

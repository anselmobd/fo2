from pprint import pprint

from o2.views.base.custom import CustomView


class O2BaseGetView(CustomView):

    def render_mount(self):
        self.mount_context()
        return self.my_render()

    def get(self, request, *args, **kwargs):
        self.init_self(request, kwargs)

        return self.render_mount()

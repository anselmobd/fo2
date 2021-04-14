from pprint import pprint

from django.shortcuts import redirect, render
from django.views import View


class CustomView(View):
    """
    Base para customizar views

    """

    def __init__(self, *args, **kwargs):
        """
        Inicializa parâmetros, sendo:
        
        get_args
            uma lista de nomes de variáveis recebidas por GET
        
        get_args2context
            um boolean indicando se as variáveis recebidas por GET
            vão para o context
        """
        super(CustomView, self).__init__(*args, **kwargs)
        self.get_args = []
        self.get_args2context = False
        self.redirect = None

    def init_self(self, request, kwargs):
        """
        Inicializa variáveis do self:
            request
            kwargs
            context
        """
        self.request = request
        self.kwargs = kwargs

        self.context = {}
        if hasattr(self, 'title_name'):
            self.context.update({'titulo': self.title_name})

        if self.get_args2context:
            for arg in self.get_args:
                arg_value = self.get_arg(arg)
                self.context.update({arg: arg_value})

    def get_arg(self, field):
        """
        Retorna Keyword Argument ou nulo
        """
        return self.kwargs[field] if field in self.kwargs else None

    def my_render(self):
        """
        Se redirect for definifo, execute.
        Senão, chama render com self: request, template_name e context
        """
        if self.redirect:
            if isinstance(self.redirect, tuple):
                return redirect(*self.redirect)
            else:
                return redirect(self.redirect)
        return render(self.request, self.template_name, self.context)

    def mount_context(self):
        """
        Metodo de montagem de contexto        
        """
        pass

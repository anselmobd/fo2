from pprint import pprint

from django.apps import apps
from django.shortcuts import redirect, render
from django.views import View


class StopStepsException(Exception):
    '''
    '''
    def __init__(self, val=""):
        self.val = val
        super().__init__()

    def __str__(self):
        return f"Passos interrompidos. Motivo: {self.val}"


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
        
        get_args2self
            um boolean indicando se as variáveis recebidas por GET
            vão para o self da view

        redirect
            string ou tupla que serão attibutos da execução de um
            redirect. Caso None, é executado um render.

        """
        super(CustomView, self).__init__(*args, **kwargs)
        self.get_args = []
        self.get_args2context = False
        self.get_args2self = False
        self.redirect = None

        self.context = {}

    def init_self(self, request, kwargs):
        """
        Inicializa variáveis do self:
            request
            kwargs
            context
            {outras, caso get_args2self}
        """
        self.request = request
        self.kwargs = kwargs

        self.app_name = request.resolver_match.app_name
        if self.app_name == 'producao':
            self.app_name = 'lotes'
        self.app_config = apps.get_app_config(self.app_name)
        self.context.update({'app_config': self.app_config})

        if hasattr(self, 'title_name'):
            self.context.update({'titulo': self.title_name})

        if self.get_args2context:
            for arg in self.get_args:
                arg_value = self.get_arg(arg)
                self.context.update({arg: arg_value})

        if self.get_args2self:
            for arg in self.get_args:
                arg_value = self.get_arg(arg)
                setattr(self, arg, arg_value)

    def get_arg(self, field):
        """
        Retorna Keyword Argument ou nulo
        """
        return self.kwargs[field] if field in self.kwargs else None

    def my_render(self):
        """
        Se self.redirect for definido, execute redirect.
        Senão, execute render com request, template_name e context
        """
        if self.redirect:
            if isinstance(self.redirect, tuple):
                return redirect(*self.redirect)
            else:
                return redirect(self.redirect)
        return render(self.request, self.template_name, self.context)

    def pre_mount_context(self):
        """
        Metodo de pré-montagem de contexto
        """
        pass

    def mount_context(self):
        """
        Metodo de montagem de contexto
        """
        pass

    def do_steps(self, steps, msg_erro='msg_erro'):
        """Metodo de que recebe lista de metodos e os executa.

        Retorna booleano indicando sucesso da execução da lista inteira.
        Na primeira ocorrência de excessão a execução da lista é interompida.
        
        Se os métodos levantarem uma exceção o texto desta vai para a chave
        msg_erro do self.context

        Se, na lista, no lugar de um método, constar um tupla, entende-se que esta 
        contenha (método, atributo).

        Na ausência de exceção, o retorno do método é atribuido ao atributo no self.

        Caso tanto o atributo quanto o retorno forem dicionários, é feito um
        atributo.update(retorno). Isso é útil, por exemplo, quando se quer que o 
        retorno seja adicionado ao context.
        """
        for do_get in steps:
            try:
                if isinstance(do_get, tuple):
                    do, attrib = do_get
                    result = do()
                    value = getattr(self, attrib, None)
                    if value:
                        if isinstance(value, dict) and isinstance(result, dict):
                            value.update(result)
                        else:
                            raise Exception(f"Atributo '{attrib}' já existe e não é caso de 'dict.update'")
                    else:
                        setattr(self, attrib, result)
                else:
                    do_get()
            except StopStepsException as e:
                self.context.update({
                    msg_erro: e,
                })
                return False
        return True

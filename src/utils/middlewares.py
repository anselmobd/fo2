import re
import threading

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from geral.functions import is_alternativa
from utils.functions import get_client_ip


request_cfg = threading.local()


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .classes import LoggedInUser, AcessoInterno


class LoggedInUserMiddleware(MiddlewareMixin):
    '''
        Insert this middleware after
        django.contrib.auth.middleware.AuthenticationMiddleware
    '''
    def process_request(self, request):
        '''
            Returned None for continue request
        '''
        logged_in_user = LoggedInUser()
        logged_in_user.set_user(request)
        return None


class NeedToLoginOrLocalMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_ip = get_client_ip(request)
        authenticated_by_ip = False
        for ip in settings.N2LOL_ALLOWED_IP_BLOCKS:
            if re.compile(ip).match(user_ip) is not None:
                authenticated_by_ip = True
                break

        acesso_interno = AcessoInterno()
        acesso_interno.set_interno(authenticated_by_ip)
        acesso_interno.set_ip(user_ip)

        if request.user.is_authenticated:
            return self.get_response(request)

        if authenticated_by_ip:
            return self.get_response(request)

        user_url = request.META['PATH_INFO']
        for url in settings.N2LOL_ALLOWED_URLS:
            if re.compile(url).match(user_url) is not None:
                return self.get_response(request)

        return redirect(settings.N2LOL_REDIRECT)


class AlterRouterMiddleware:
    """
    Based on
    https://gist.github.com/gijzelaerr/7a3130c494215a0dd9b2/
    
    The Alternative db router middelware.

    Before the view sets some context from the URL into thread local storage.
    After, deletes it.
    
    In between, any database operation will call the router, which checks for
    the thread local storage and returns an appropriate database alias.

    Add this to your middleware, for example:

    MIDDLEWARE += ['utils.middlewares.AlterRouterMiddleware']
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request_cfg.alter_db = is_alternativa(request)
        request.alter_db = request_cfg.alter_db

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if hasattr(request_cfg, 'alter_db'):
            del request_cfg.alter_db

        return response

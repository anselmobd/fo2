import re

from django.shortcuts import redirect

from fo2 import settings


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .classes import LoggedInUser


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
        if request.user.is_authenticated:
            return self.get_response(request)

        user_ip = request.META['REMOTE_ADDR']
        authenticated_by_ip = False
        for ip in settings.N2LOL_ALLOWED_IP_BLOCKS:
            authenticated_by_ip = \
                authenticated_by_ip or \
                (re.compile(ip).match(user_ip) is not None)

        if authenticated_by_ip:
            return self.get_response(request)

        user_url = request.META['PATH_INFO']
        liberated_by_url = False
        for url in settings.N2LOL_ALLOWED_URLS:
            liberated_by_url = \
                liberated_by_url or \
                (re.compile(url).match(user_url) is not None)

        if liberated_by_url:
            return self.get_response(request)

        return redirect(settings.N2LOL_REDIRECT)

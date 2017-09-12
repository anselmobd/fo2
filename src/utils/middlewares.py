try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .classes import LoggedInUser


# def logged_in_user_middleware(get_response):
#     '''
#         Insert this middleware after
#         django.contrib.auth.middleware.AuthenticationMiddleware
#     '''
#     def middleware(request):
#         '''
#             Returned None for continue request
#         '''
#         logged_in_user = LoggedInUser()
#         logged_in_user.set_user(request)
#         return None
#     return middleware


# class LoggedInUserMiddleware(object):
#     '''
#         Insert this middleware after
#         django.contrib.auth.middleware.AuthenticationMiddleware
#     '''
#     def process_request(self, request):
#         '''
#             Returned None for continue request
#         '''
#         logged_in_user = LoggedInUser()
#         logged_in_user.set_user(request)
#         return None

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

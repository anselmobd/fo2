class SingletonMeta(type):
    '''
        Singleton pattern requires for GetUser class
    '''
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance


class SingletonBaseMeta(metaclass=SingletonMeta):
    pass


class NotLoggedInUserException(Exception):
    '''
    '''
    def __init__(self, val='No users have been logged in'):
        self.val = val
        super(NotLoggedInUser, self).__init__()

    def __str__(self):
        return self.val


class LoggedInUser(SingletonBaseMeta):

    user = None

    def set_user(self, request):
        if request.user.is_authenticated():
            self.user = request.user

    @property
    def current_user(self):
        '''
            Return current user or raise Exception
        '''
        if self.user is None:
            raise NotLoggedInUserException()
        return self.user

    @property
    def have_user(self):
        return user is not None

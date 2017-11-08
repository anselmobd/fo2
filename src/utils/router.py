class Router(object):
    """
    A router to control all database operations on models.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'systextil':
            return 'so'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'systextil':
            return 'so'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'systextil' or \
           obj2._meta.app_label == 'systextil':
            return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'systextil':
            return False
        return True

from utils.middlewares import request_cfg


class Router(object):
    """
    A router to control all database operations on models.
    """

    def systextil_conn(self):
        if hasattr(request_cfg, 'alter_db') and request_cfg.alter_db:
            return 'sn'
        else:
            return 'so'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'systextil':
            return self.systextil_conn()
        return 'default'

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'systextil' and \
           obj2._meta.app_label == 'systextil':
            return True
        elif 'systextil' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'systextil':
            return db == 'so'
        elif db == 'so':
            return False
        return None

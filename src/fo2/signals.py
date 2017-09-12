from pprint import pprint
import difflib

from utils.classes import LoggedInUser
from geral.models import RecordTracking


def post_init_tracking(sender, instance, **kwargs):
    '''
        Signal post_init to track record changes, if record has id field.
        Work in conjunction with post_save_tracking.
    '''
    print('--- post_init_tracking', sender.__name__)
    # pprint(sender.__dict__)
    # pprint(instance.__dict__)
    # pprint(kwargs)
    if hasattr(instance, 'id'):
        original = {}
        for field in sender._meta.get_fields():
            if hasattr(instance, field.name):
                original[field.name] = getattr(instance, field.name)
        setattr(instance, '__original_record_values', original)


def post_save_tracking(sender, instance, **kwargs):
    '''
        Signal post_save to track record changes, if record has id field.
        Work in conjunction with post_init_tracking.
    '''
    print('--- post_save_tracking', sender.__name__)
    # pprint(sender.__dict__)
    # pprint(instance.__dict__)
    # pprint(kwargs)
    if hasattr(instance, '__original_record_values'):
        logged_in = LoggedInUser()
        user = logged_in.user
        print('user = {}'.format(user))
        original = getattr(instance, '__original_record_values')
        if original['id'] == getattr(instance, 'id'):
            altered = {}
            for k in original:
                old = original[k]
                new = getattr(instance, k)
                if k == 'id' or new != old:
                    altered[k] = new
                    if new is not None and old is not None and \
                            (isinstance(old, str) or isinstance(new, str)):
                        old_s = old.splitlines(keepends=True)
                        new_s = new.splitlines(keepends=True)

                        diff = difflib.unified_diff(
                            old_s, new_s, n=0, lineterm='\r\n')
                        lindiff = ''.join([l for l in diff])

                        # the "+10" is to compensate the ".__delta__"
                        if (len(lindiff)+10) < len(new):
                            altered[k+'.__delta__'] = lindiff
            print('{} altered = {}'.format(sender.__name__, altered))
            rt = RecordTracking()
            rt.user = user
            rt.table = sender.__name__
            rt.record_id = altered['id']
            rt.iud = 'u'
            rt.log = altered
            rt.save()
            print('rt.user = {}'.format(rt.user))
        else:
            record = {}
            for field in sender._meta.get_fields():
                if hasattr(instance, field.name):
                    record[field.name] = getattr(instance, field.name)
            print('{} inserted = {}'.format(sender.__name__, record))
            rt = RecordTracking()
            rt.user = user
            rt.table = sender.__name__
            rt.record_id = record['id']
            rt.iud = 'i'
            rt.log = record
            rt.save()
            print('rt.user = {}'.format(rt.user))


def post_delete_tracking(sender, instance, **kwargs):
    '''
        Signal post_delete to track record deletions, if record has id field.
        Work in conjunction with post_init_tracking.
    '''
    print('--- post_delete_tracking', sender.__name__)
    # pprint(sender.__dict__)
    # pprint(instance.__dict__)
    # pprint(kwargs)
    if hasattr(instance, 'id'):
        logged_in = LoggedInUser()
        user = logged_in.user
        print('user = {}'.format(user))
        record = {}
        record['id'] = getattr(instance, 'id')
        rt = RecordTracking()
        rt.user = user
        rt.table = sender.__name__
        rt.record_id = record['id']
        rt.iud = 'd'
        rt.log = record
        rt.save()
        print('{} deleted = {}'.format(sender.__name__, record))

from pprint import pprint
import difflib

from utils.classes import LoggedInUser


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
                v_new = getattr(instance, k)
                if k == 'id' or v_new != original[k]:
                    if isinstance(original[k], str) or isinstance(v_new, str):
                        old = original[k].splitlines(keepends=True)
                        new = v_new.splitlines(keepends=True)

                        diff = difflib.unified_diff(
                            old, new, n=0, lineterm='\r\n')
                        lindiff = ''.join([l for l in diff])

                        # the "+10" is to compensate the ".__delta__"
                        if (len(lindiff)+10) < len(v_new):
                            altered[k+'.__delta__'] = lindiff
                        else:
                            altered[k] = v_new
                    else:
                        altered[k] = v_new
            print('{} altered = {}'.format(sender.__name__, altered))
        else:
            record = {}
            for field in sender._meta.get_fields():
                if hasattr(instance, field.name):
                    record[field.name] = getattr(instance, field.name)
            print('{} inserted = {}'.format(sender.__name__, record))


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
        print('{} deleted = {}'.format(sender.__name__, record))

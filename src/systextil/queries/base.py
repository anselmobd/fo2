from pprint import pprint

from fo2.connections import db_cursor_so

from o2.queries import MountQuery, OQuery


class SMountQuery(MountQuery):

    def __init__(self, *args, **kwargs) -> None:
        super(SMountQuery, self).__init__(*args, **kwargs)
        self._OQuery = SOQuery


class SOQuery(OQuery):

    def __init__(self, *args, **kwargs) -> None:
        super(SOQuery, self).__init__(*args, **kwargs)
        self._cursor = db_cursor_so()

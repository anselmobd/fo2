from pprint import pprint
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.functions import coalesce


class MyPaginator(Paginator):
    def __init__(self, *args, pag_neib=None, **kwargs):
        self.__pag_neib = coalesce(pag_neib, 5)
        super().__init__(*args, **kwargs)

    @property
    def pag_neib(self):
        return self.__pag_neib


def paginator_basic(data, nrows, page, pag_neib=None):
    paginator = MyPaginator(data, nrows, pag_neib=pag_neib)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

from pprint import pprint
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginator_basic(data, nrows, page):
    paginator = Paginator(data, nrows)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

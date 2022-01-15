import requests
from pprint import pprint

from utils.functions import acesso_externo


def get_sessions():
    urls = [
        "http://oc.tussor.com.br/systextil/sessions",
        "http://tussor.systextil.com.br/systextil/sessions",
    ]
    if acesso_externo():
        urls.reverse()
    for u in urls:
        try:
            req = requests.get(u, timeout=10)
        except requests.exceptions.ConnectTimeout:
            continue
        if req.status_code == 200:
            return req.json()
    return {}

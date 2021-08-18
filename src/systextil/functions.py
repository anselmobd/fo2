import requests
from pprint import pprint


def get_sessions():
    urls = [
        "http://oc.tussor.com.br/systextil/sessions",
        "http://tussor.systextil.com.br/systextil/sessions",
    ]
    for u in urls:
        try:
            req = requests.get(u, timeout=10)
        except requests.exceptions.ConnectTimeout:
            continue
        if req.status_code == 200:
            return req.json()
    return {}

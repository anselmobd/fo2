from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse

from utils.functions import get_client_ip


class IndexView(TemplateView):
    template_name = "index.html"


class IntranetView(TemplateView):
    template_name = "intranet.html"


def logout_view(request):
    logout(request)
    return redirect('/')


def myip_view(request):
    return HttpResponse("Your IP is : {}".format(get_client_ip(request)))

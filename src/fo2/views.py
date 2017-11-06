from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect


class IndexView(TemplateView):
    template_name = "index.html"


class IntranetView(TemplateView):
    template_name = "intranet.html"


def logout_view(request):
    logout(request)
    return redirect('/')

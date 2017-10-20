from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.shortcuts import redirect


class IndexView(TemplateView):
    template_name = "index.html"


class InfoView(TemplateView):
    template_name = "info.html"


def logout_view(request):
    logout(request)
    return redirect('/')

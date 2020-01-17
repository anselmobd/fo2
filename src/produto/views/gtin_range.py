from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from produto.models import GtinRange


class GtinRangeListView(ListView):
    model = GtinRange
    context_object_name = 'gtinranges'


class GtinRangeCreateView(CreateView):
    model = GtinRange
    fields = ('ordem', 'pais', 'codigo')
    success_url = reverse_lazy('produto:gtinrange_changelist')


class GtinRangeUpdateView(UpdateView):
    model = GtinRange
    fields = ('ordem', 'pais', 'codigo')
    success_url = reverse_lazy('produto:gtinrange_changelist')


class GtinRangeDeleteView(DeleteView):
    model = GtinRange
    success_url = reverse_lazy('produto:gtinrange_changelist')

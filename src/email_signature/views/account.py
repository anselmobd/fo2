from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from email_signature.models import Account


class AccountListView(ListView):
    model = Account
    context_object_name = 'accounts'


class AccountCreateView(CreateView):
    model = Account
    fields = ('email', 'nome', 'setor', 'num_1', 'num_2', 'dir_servidor')
    success_url = reverse_lazy('email_signature:account_list')


class AccountUpdateView(UpdateView):
    model = Account
    fields = ('email', 'nome', 'setor', 'num_1', 'num_2', 'dir_servidor')
    success_url = reverse_lazy('email_signature:account_list')


class AccountDeleteView(DeleteView):
    model = Account
    success_url = reverse_lazy('email_signature:account_list')

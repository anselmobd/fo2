from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from email_signature.models import Account


class AccountListView(ListView):
    model = Account
    context_object_name = 'emsign_accounts'


class AccountCreateView(CreateView):
    model = Account
    fields = ('codigo', 'nome', 'setor', 'email', 'tipo_num_1', 'num_1',
              'tipo_num_2', 'num_2', 'dir_servidor', 'dir_local')
    success_url = reverse_lazy('produto:emsign_account_changelist')


class AccountUpdateView(UpdateView):
    model = Account
    fields = ('codigo', 'nome', 'setor', 'email', 'tipo_num_1', 'num_1',
              'tipo_num_2', 'num_2', 'dir_servidor', 'dir_local')
    success_url = reverse_lazy('produto:emsign_account_changelist')


class AccountDeleteView(DeleteView):
    model = Account
    success_url = reverse_lazy('produto:emsign_account_changelist')

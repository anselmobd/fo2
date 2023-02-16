from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin
    )
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

import email_signature.forms
from email_signature.models import Account


class AccountListView(PermissionRequiredMixin, ListView):

    def __init__(self):
        self.permission_required = 'email_signature.can_edit_mail_signature'
        self.model = Account
        self.context_object_name = 'accounts'
        self.ordering = ['tipo', 'email']
        self.paginate_by = 100
        super().__init__()

    def get_queryset(self):
        object_list = self.model.objects

        query = self.request.GET.get('q')
        queries = query.split(' ') if query else []

        for q in queries:
            if q:
                object_list = object_list.filter(
                    Q(tipo__icontains=q) |
                    Q(email__icontains=q) |
                    Q(nome__icontains=q) |
                    Q(setor__icontains=q)
                )
        else:
            object_list = object_list.all()

        return object_list.order_by(*self.ordering)

class AccountCreateView(PermissionRequiredMixin, CreateView):

    def __init__(self):
        self.permission_required = 'email_signature.can_edit_mail_signature'
        self.model = Account
        self.form_class = email_signature.forms.AccountForm
        self.success_url = reverse_lazy('email_signature:account_list')
        super().__init__()


class AccountUpdateView(PermissionRequiredMixin, UpdateView):

    def __init__(self):
        self.permission_required = 'email_signature.can_edit_mail_signature'
        self.model = Account
        self.form_class = email_signature.forms.AccountForm
        self.success_url = reverse_lazy('email_signature:account_list')
        super().__init__()


class AccountDeleteView(PermissionRequiredMixin, DeleteView):

    def __init__(self):
        self.permission_required = 'email_signature.can_edit_mail_signature'
        self.model = Account
        self.success_url = reverse_lazy('email_signature:account_list')
        super().__init__()

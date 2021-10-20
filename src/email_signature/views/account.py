from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    LoginRequiredMixin
    )
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

import email_signature.forms
from email_signature.models import Account


class AccountListView(PermissionRequiredMixin, ListView):
    permission_required = 'email_signature.can_edit_mail_signature'
    model = Account
    context_object_name = 'accounts'
    ordering = ['email']


class AccountCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'email_signature.can_edit_mail_signature'
    model = Account
    form_class = email_signature.forms.AccountForm
    success_url = reverse_lazy('email_signature:account_list')


class AccountUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'email_signature.can_edit_mail_signature'
    model = Account
    form_class = email_signature.forms.AccountForm
    success_url = reverse_lazy('email_signature:account_list')


class AccountDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'email_signature.can_edit_mail_signature'
    model = Account
    success_url = reverse_lazy('email_signature:account_list')

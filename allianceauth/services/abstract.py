"""
Abstract view classes for building services.

These view classes are provided as convenience only. If they
don't make sense to use in your service, there is no obligation
to use these views. You are free to build the internal structure
of the service as you like.
"""

from collections import OrderedDict
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, Http404, redirect

from .forms import ServicePasswordModelForm

import logging

logger = logging.getLogger(__name__)


class AbstractServiceModel(models.Model):
    user = models.OneToOneField('auth.User',
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='%(app_label)s'
                                )

    def __init__(self, *args, **kwargs):
        super(AbstractServiceModel, self).__init__(*args, **kwargs)
        self.credentials = OrderedDict()
        # Should be set with a dict of service credentials (username, password etc) when changed

    def update_password(self, password=None):
        pass

    def reset_password(self):
        pass

    class Meta:
        abstract = True


class BaseServiceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Define:
        permission_required
    """
    index_redirect = 'services:services'
    success_url = reverse_lazy(index_redirect)
    model = AbstractServiceModel  # Overload
    service_name = 'base'  # Overload


class ServiceCredentialsViewMixin:
    template_name = 'services/service_credentials.html'


class BaseCreatePasswordServiceAccountView(BaseServiceView, ServiceCredentialsViewMixin):
    def get(self, request):
        logger.debug("{} called by user {}".format(self.__class__.__name__, request.user))
        try:
            svc_obj = self.model.objects.create(user=request.user)
        except IntegrityError:
            messages.error(request, "That service account already exists")
            return redirect(self.index_redirect)

        return render(request, self.template_name,
                      context={'credentials': svc_obj.credentials, 'service': self.service_name, 'view': self})


class ServicesCRUDMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        """
        if queryset is None:
            queryset = self.get_queryset()

        try:
            return queryset.get(user__pk=self.request.user.pk)
        except ObjectDoesNotExist:
            raise Http404


class BaseDeactivateServiceAccountView(ServicesCRUDMixin, BaseServiceView, DeleteView):
    template_name = 'services/service_confirm_delete.html'


class BaseSetPasswordServiceAccountView(ServicesCRUDMixin, BaseServiceView, UpdateView):
    template_name = 'services/service_password.html'
    form_class = ServicePasswordModelForm  # You should overload this with a subclass

    def post(self, request, *args, **kwargs):
        result = super(BaseSetPasswordServiceAccountView, self).post(request, *args, **kwargs)
        if self.get_form().is_valid():
            messages.success(request, "Successfully set your {} password".format(self.service_name))
        return result


class BaseResetPasswordServiceAccountView(ServicesCRUDMixin, BaseServiceView, ServiceCredentialsViewMixin):
    """
    Set a random password
    """
    def get(self, request):
        svc_obj = self.get_object()
        svc_obj.reset_password()
        return render(request, self.template_name,
                      context={'credentials': svc_obj.credentials, 'service': self.service_name, 'view': self})

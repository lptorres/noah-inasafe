#layer_manager/views.py
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django import forms

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from .models import Layer
from .forms import LayerUploadForm


class LayerUploadActionMixin(object):

    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)

    def form_valid(self, form):
        msg = "Layer {0}!".format(self.action)
        messages.info(self.request, msg)
        return super(LayerUploadActionMixin, self).form_valid(form)


class LayerUploadView(LoginRequiredMixin, PermissionRequiredMixin,
    LayerUploadActionMixin, CreateView):

    permission_required = "auth.change_user"
    model = Layer
   # form_class = LayerUploadForm 
    action = "uploaded"


class LayerListView(ListView):

    model = Layer


class LayerDetailView(DetailView):

    model = Layer

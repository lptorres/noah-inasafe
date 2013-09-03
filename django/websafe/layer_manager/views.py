"""

layer_manager/views.py

Contains views the determine what content the users will see for the 
websafe project.

"""


from django import forms
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from layer_manager.models import Layer
from layer_manager.forms import LayerUploadForm


class LayerUploadActionMixin(object):
    """
    This is just a mixin that displays if the user did not complete an action
    when uploading a layer, or if the upload was successful.
    """
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
    """
    Displays a form that creates a new instance of a Layer object after being
    accomplished, and saves that instance into the database.
    Unless the template path and name are specified, Django will look for the
    'layer_form.html' template in all of the template directories configured
    in the settings file.
    The form_class attribute is set to 'LayerUploadForm' which performs custom
    validation.
    """
    permission_required = "auth.change_user"
    model = Layer
    form_class = LayerUploadForm 
    action = "uploaded"


class LayerListView(ListView):
    """
    Displays the list of all Layer objects.
    Unless the template path and name are specified, Django will look for the
    'layer_list.html' template in all of the template directories configured
    in the settings file.
    """
    model = Layer


class LayerDetailView(DetailView):
    """
    Displays the details of a specific layer object.
    Unless the template path and name are specified, Django will look for the
    'layer_detail.html' template in all of the template directories configured
    in the settings file.
    """
    model = Layer

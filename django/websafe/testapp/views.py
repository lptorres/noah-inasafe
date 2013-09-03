from django.views.generic import DetailView, CreateView

from .models import TestModel

class MyCreateView(CreateView):
    model = TestModel


class MyDetailView(DetailView):
    model = TestModel

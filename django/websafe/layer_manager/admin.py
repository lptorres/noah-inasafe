from django.contrib import admin
from .models import Layer
from testapp.models import TestModel

admin.site.register(Layer)
admin.site.register(TestModel)

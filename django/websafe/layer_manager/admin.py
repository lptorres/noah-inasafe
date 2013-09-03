"""

layer_manager/admin.py

This just tells Django's built-in admin site to include the Layer model.

"""

from django.contrib import admin

from layer_manager.models import Layer

admin.site.register(Layer)
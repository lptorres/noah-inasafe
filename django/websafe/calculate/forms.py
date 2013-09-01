from django import forms

from layer_manager.models import Layer

class CalculateForm(forms.Form):
    
    exposure_choices = []
    hazard_choices = []
    
    for layer in Layer.objects.all():
        if layer.layer_category == 'E':
            tmp = ( str(layer.slug), str(layer.name) )
            exposure_choices.append(tmp)
        else:
            tmp = ( str(layer.slug), str(layer.name) )
            hazard_choices.append(tmp)
        
    exposure = forms.ChoiceField(choices=exposure_choices)
    hazard = forms.ChoiceField(choices=hazard_choices)
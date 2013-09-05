#calculate/forms.py
from django import forms

from layer_manager.models import Layer

class CalculateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CalculateForm, self).__init__(*args, **kwargs)
        print 'Initializing your form...'
        
        exposure_choices = [('-','-'),]
        hazard_choices = [('-','-'),]
        
        for layer in Layer.objects.all():
            tmp = (str(layer.slug),str(layer.name))
            if layer.layer_category == 'E':
                exposure_choices.append(tmp)
            else:
                hazard_choices.append(tmp)
                
        self.fields['exposure'] = forms.ChoiceField(choices=exposure_choices)
        self.fields['hazard'] = forms.ChoiceField(choices=hazard_choices)
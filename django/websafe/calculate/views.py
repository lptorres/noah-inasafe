import glob
import os
from subprocess import call

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, TemplateView

from safe.api import read_layer
from safe.api import calculate_impact
from safe.impact_functions.inundation.flood_OSM_building_impact \
    import FloodBuildingImpactFunction
from calculate.forms import CalculateForm
from layer_manager.models import Layer

        
class CalculateView(FormView):
    template_name = 'calculate.html'
    form_class = CalculateForm
    success_url = '/'
    
    def form_valid(self, form):
        exp = form.cleaned_data['exposure']
        haz = form.cleaned_data['hazard']
        self.success_url = '/calculate/results&exp=%s&haz=%s' % (exp, haz)
        return super(CalculateView, self).form_valid(form)


def get_layer_data(layer_slug):
    layer = Layer.objects.get(slug=layer_slug)
    layer_path = str(os.path.join(
        settings.MEDIA_ROOT, 'layers', layer.slug, 'raw'))
    os.chdir(layer_path)
    filename = glob.glob('*.shp')[0]
    layer_file = str(os.path.join(layer_path, filename))
    return read_layer(layer_file)

        
class ResultsView(TemplateView):
    template_name = 'results.html'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)

        exposure_slug = self.kwargs['exp']
        exposure = get_layer_data(exposure_slug)
        hazard_slug = self.kwargs['haz']
        hazard = get_layer_data(hazard_slug)
            
        exposure.keywords['category'] = 'exposure'
        exposure.keywords['subcategory'] = 'structure'
        hazard.keywords['category'] = 'hazard'
        hazard.keywords['subcategory'] = 'flood'
        
        outname = 'impact%s%s.json' % (exposure_slug, hazard_slug)
        output = os.path.join(settings.MEDIA_ROOT, 'layers', outname)
        
        impact_function = FloodBuildingImpactFunction
        
        # run analysis
        impact_file = calculate_impact(
            layers=[exposure, hazard],
            impact_fcn=impact_function
        )

        call(['ogr2ogr', '-f', 'GeoJSON',
              output, impact_file.filename])

        impact_geojson = os.path.join(settings.MEDIA_URL, 'layers', outname)

        context = impact_file.keywords
        context['geojson'] = impact_geojson
        
        return context
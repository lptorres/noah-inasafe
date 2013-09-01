from calculate.forms import CalculateForm
from django.views.generic import FormView, TemplateView
from django.shortcuts import get_object_or_404
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
        
class TestView(TemplateView):
    template_name = 'results.html'
    
    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['haz'] = self.kwargs['haz']
        context['exp'] = self.kwargs['exp']
        print self.kwargs['regex']
        return context
        
class ResultsView(TemplateView):
    template_name = 'results.html'

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)

        context['exp'] = get_object_or_404(Layer, 
            slug__iexact=self.kwargs['exp'])
        context['haz'] = get_object_or_404(Layer, 
            slug__iexact=self.kwargs['haz'])
        
        return context
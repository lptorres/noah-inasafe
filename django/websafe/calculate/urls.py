#calculate/urls.py
from django.conf.urls import patterns, include, url
from calculate.views import CalculateView, ResultsView

urlpatterns = patterns('',
    url(r'^$', CalculateView.as_view(), name='calculate'),
    url(r'^results&exp=(?P<exp>[\w-]+)&haz=(?P<haz>[\w-]+)/$', 
        ResultsView.as_view(), name='results'),
)
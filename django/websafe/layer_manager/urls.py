#tournament_start/urls.py
from django.conf.urls import patterns, include, url
from views import LayerUploadView, LayerListView, LayerDetailView

urlpatterns = patterns('',
    url(r'^$', LayerListView.as_view(), name='index'),
    url(r'^upload/$', LayerUploadView.as_view(), name='upload'),
    url(r'^(?P<slug>[\w-]+)/$', LayerDetailView.as_view(), 
        name='detail'),
)


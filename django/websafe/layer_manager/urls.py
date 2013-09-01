#tournament_start/urls.py
from django.conf.urls import patterns, include, url
from views import LayerUploadView, LayerListView, LayerDetailView

urlpatterns = patterns('',
    url(r'^upload/$', LayerUploadView.as_view(), name='layer_upload'),
    url(r'^/$', LayerListView.as_view(), name='layer_index'),
    url(r'^(?P<slug>[\w-]+)/$', LayerDetailView.as_view(), 
        name='layer_detail'),
)


from django.conf.urls import patterns, include, url
from testapp.views import MyCreateView, MyDetailView

urlpatterns = patterns('',
    url(r'^create/$', MyCreateView.as_view(), name='my_create'),
    url(r'^(?P<slug>[\w-]+)/$', MyDetailView.as_view(), name='my_detail'),
)

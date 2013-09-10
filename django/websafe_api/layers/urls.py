from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from layers import views

urlpatterns = format_suffix_patterns(patterns('',
    url(r'^layers/$', views.LayerList.as_view()),
    url(r'^layers/(?P<pk>[0-9]+)/$', views.LayerDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
))
"""

Entry point for web requests in websafe project.

"""
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin, auth
from django.views.generic import TemplateView

import smart_selects

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='homepage.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('account.urls')),
    url(r'^layers/', include('layer_manager.urls', namespace='layers')),
    url(r'^calculate/', include('calculate.urls', namespace='calculate')),
    url(r'^account/login$', "django.contrib.auth.views.login"),
    url(r'^chaining/', include('smart_selects.urls')),
)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

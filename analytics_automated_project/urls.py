"""analytics_automated_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from analytics_automated import views

from analytics_automated.api import SubmissionResource

urlpatterns = [
     url(r'^admin/', include(admin.site.urls)),
     url(r'^analytics_automated/', include('analytics_automated.urls')),
]

# At the top of your urls.py file, add the following line:

# UNDERNEATH your urlpatterns definition, add the following two lines:
if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
                            (
                                r'^submissions/(?P<path>.*)', 'serve',
                                {'document_root': settings.MEDIA_ROOT}
                            ),
                            )

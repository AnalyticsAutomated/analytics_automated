from django.conf.urls import patterns, include, url
from django.contrib import admin
from analytics_automated import views

urlpatterns = [
     url(r'^$', views.index, name='index'),
 ]

from django.conf.urls import patterns, include, url
from django.contrib import admin

from .api import SubmissionDetail, SubmissionList, SubmissionData

urlpatterns = [
    url(r'^submission/$', SubmissionList.as_view(), name='submission_list'),
    url(r'^submission/(?P<pk>\d+)', SubmissionDetail.as_view(), name='submission_detail'),
    url(r'^submission/create', SubmissionData.as_view(), name='submission_data'),

]

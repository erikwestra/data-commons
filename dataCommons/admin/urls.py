""" dataCommons.admin.urls

    This module defines the URLs for the admin application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.admin.views',
    ('^$',                     'main'),
    ('^reports/postingQueue$', 'posting_queue_report'),
)


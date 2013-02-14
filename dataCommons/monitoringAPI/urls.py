""" dataCommons.monitoringAPI.urls

    This module defines the URLs for the Monitoring API application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.monitoringAPI.views',
    ('^record/$', 'record'),
)


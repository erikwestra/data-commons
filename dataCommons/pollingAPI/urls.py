""" dataCommons.pollingAPI.urls

    This module defines the URLs for the Polling API application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.pollingAPI.views',
    ('^$', 'poll'),
)


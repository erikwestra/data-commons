""" dataCommons.pollingAPI.urls

    This module defines the URLs for the "pollingAPI" application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.pollingAPI.views',
    ('^$', 'poll'),
)


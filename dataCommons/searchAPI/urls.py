""" dataCommons.searchAPI.urls

    This module defines the URLs for the Search API application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.searchAPI.views',
    ('^$', 'search'),
)


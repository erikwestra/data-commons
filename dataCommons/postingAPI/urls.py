""" dataCommons.postingAPI.urls

    This module defines the URLs for the Posting API application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.postingAPI.views',
    ('^$', 'post'),
)


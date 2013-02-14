""" dataCommons.summarizerAPI.urls

    This module defines the URLs for the Summarizer API application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.summarizerAPI.views',
    ('^$', 'summarize'),
)


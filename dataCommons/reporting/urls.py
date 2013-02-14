""" dataCommons.reporting.urls

    This module defines the URLs for the Reporting application.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = patterns('dataCommons.reporting.views',
    (r'^$',         'list.list'),
    (r'^get_data$', 'get_data.get_data'),
    (r'^generate$', 'generate.generate'),
)


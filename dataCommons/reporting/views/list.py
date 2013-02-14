""" dataCommons.reporting.views.list

    This module implements the "list" view used by the Reporting application.
"""
import logging

from django.shortcuts import render_to_response
from django.template  import RequestContext

from dataCommons.reporting.reportModules import REPORT_MODULES

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def list(request):
    """ Respond to the main "/reporting" URL.

        We display a list of the available report types.
    """
    reports = []
    for module in REPORT_MODULES:
        defaults = []
        for param in module.params:
            if "default" in param:
                defaults.append(param['name'] + "=" + str(param['default']))

        url = "/reporting/generate?type=" + module.type
        if len(defaults) > 0:
            url = url + "&" + "&".join(defaults)

        reports.append((module.name, module.description, url))

    return render_to_response("reporting/templates/list.html",
                              {'reports' : reports},
                              context_instance=RequestContext(request))


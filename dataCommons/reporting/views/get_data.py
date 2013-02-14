""" dataCommons.reporting.views.get_data

    This module implements an AJAX handler that is called by Javascript code on
    the "generate" page to obtain the data to use for a report.
"""
import logging
import traceback

import simplejson as json

from django.http import HttpResponse

from dataCommons.shared.lib.decorators import *
from dataCommons.shared.lib import reportHelpers

from dataCommons.reporting.reportModules import REPORT_MODULES

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def get_data(request):
    """ Respond to the "/reporting/get_data" URL.

        We extract the supplied parameters and run the report, returning the
        generated report data in JSON format.
    """
    if request.method == "GET":
        query_params = request.GET
    elif request.method == "POST":
        query_params = request.POST
    else:
        return HttpResponse("Unsuported HTTP method: " + request.method)

    # Get the type of report to generate.

    if "type" in query_params:
        report_type = query_params['type']
    else:
        return HttpResponse("Missing required 'type' parameter.")

    # Get the caller's time-zone offset.

    if "tzoffset" in query_params:
        timezone_offset = float(query_params['tzoffset'])
    else:
        timezone_offset = None

    # Find the report definition module for this type of report.

    found = False
    for module in REPORT_MODULES:
        if report_type == module.type:
            found = True
            break

    if not found:
        return HttpResponse("Invalid report type: " + report_type)

    # Get the parameter values to use when generating this report.

    params = {}
    for param in module.params:
        if param['name'] in query_params:
            params[param['name']] = query_params[param['name']]

    # Attempt to generate the report.

    try:
        success,response = module.generator(params, timezone_offset)
    except reportHelpers.InvalidTimeframe,e:
        success  = False
        response = e.message
    except Exception,e:
        traceback.print_exc()
        success  = False
        response = str(e)

    # Finally, return the results back to the caller.

    if success:
        payload = {'success' : True,
                   'data'    : response}
    else:
        payload = {'success' : False,
                   'error'   : response}

    return HttpResponse(json.dumps(payload), mimetype="application/json")


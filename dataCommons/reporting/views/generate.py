""" dataCommons.reporting.views.generate

    This module implements the "generate" view used by the Reporting
    application.
"""
import logging

from django.http      import HttpResponse
from django.shortcuts import render_to_response
from django.template  import RequestContext

from dataCommons.reporting.reportModules import REPORT_MODULES

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

def generate(request):
    """ Respond to the "/reporting/generate" URL.

        We let the user enter the report parameters and generate a report.
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

    # Find the report definition module for this type of report.

    found = False
    for module in REPORT_MODULES:
        if report_type == module.type:
            found = True
            break

    if not found:
        return HttpResponse("Invalid report type: " + report_type)

    # Get the parameters to use for this report.  We take each parameter value
    # from the supplied query parameters, so that we can generate saved reports
    # simply by passing the appropriate query parameters.

    params = []
    for param_def in module.params:
        param = {}
        param['name']     = param_def['name']
        param['label']    = param_def['label']
        param['required'] = param_def.get("required", False)
        param['type']     = param_def['type']
        param['choices']  = param_def.get("choices", None)
        param['value']    = query_params.get(param['name'])

        if param['type'] == "timeframe" and param['value'] != None:
            s1  = ""
            s2 = ""
            for i,char in enumerate(param['value']):
                if not char.isdigit():
                    s1 = param['value'][:i]
                    s2 = param['value'][i:]
                    break

            try:
                param['num_periods'] = int(s1)
            except ValueError:
                param['num_periods'] = 0
            param['period_size'] = s2.lower()

        params.append(param)

    # Get the other information we need 

    return render_to_response("reporting/templates/generate.html",
                              {'report_type' : module.type,
                               'report_name' : module.name,
                               'description' : module.description,
                               'params'      : params,
                               'renderer'    : module.renderer,
                              },
                              context_instance=RequestContext(request))

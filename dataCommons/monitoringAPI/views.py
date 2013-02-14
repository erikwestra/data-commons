""" dataCommons.monitoringAPI.views

    This module defines the various view functions for the 3taps Monitoring
    API.
"""
import logging

from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt

import simplejson as json

from dataCommons.monitoringAPI import event_recorder

from dataCommons.monitoringAPI.reports import posting_queue_report

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

@csrf_exempt
def record(request):
    """ Respond to the "/api/latest/monitoring/record" URL.

        We record a new event based on the supplied parameters.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    params = request.POST

    # Check the caller's authentication.

    # ...eventually.

    # Get our event parameters.

    if "source" in params:
        source = params['source']
    else:
        return HttpResponseBadRequest("Missing required 'source' parameter")

    if "type" in params:
        type = params['type']
    else:
        return HttpResponseBadRequest("Missing required 'type' parameter")

    if "primary_value" in params:
        primary_value = params['primary_value']
    else:
        primary_value = None

    if "secondary_value" in params:
        secondary_value = params['secondary_value']
    else:
        secondary_value = None

    if "text" in params:
        text = params['text']
    else:
        text = None

    # Add the event to the system.

    err_msg = event_recorder.record(source, type,
                                    primary_value, secondary_value, text)

    if err_msg == None:
        return HttpResponse("OK")
    else:
        return HttpResponse(err_msg)


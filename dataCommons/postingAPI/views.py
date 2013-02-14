""" dataCommons.postingAPI.views

    This module defines the view functions made available by the "PostingAPI"
    application.
"""
import os
import random
import logging

from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt

from django.db.models import *

import simplejson as json

from dataCommons.shared.models         import *
from dataCommons.shared.lib.decorators import *
from dataCommons.shared.lib            import eventRecorder

from dataCommons.monitoringAPI.models import *

from dataCommons.postingAPI import postingParser
from dataCommons.postingAPI import tasks

#############################################################################

logger = logging.getLogger(__name__)

#############################################################################

@csrf_exempt
@print_exceptions_to_stdout_and_return_500
def post(request):
    """ Respond to the "/api/latest/posting" URL.

        We accept a number of postings and add them to the database.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if request.META['CONTENT_TYPE'] != "application/json":
        return HttpResponseBadRequest("Request not in JSON format")

    try:
        params = json.loads(request.body)
    except:
        return HttpResponseBadRequest("Invalid JSON data")

    # Check the caller's authentication.

    # ...eventually.

    # Grab the raw posting data supplied by the caller.

    if "posting" in params:
        raw_postings = [params['posting']]
    elif "postings" in params:
        raw_postings = params['postings']
    else:
        return HttpResponseBadRequest("Missing 'posting' or 'postings' " +
                                      "parameter")

    if len(raw_postings) > 1000:
        return HttpResponseBadRequest("Too many postings")

    # Check the raw postings, making sure the supplied data is valid.  We
    # generate two lists: a list of checked postings to process, and a list of
    # responses to send back to the caller.

    results = postingParser.check_raw_postings(raw_postings)

    error_responses = []
    postings        = []

    for success,result in results:
        if success:
            error_responses.append(None)
            postings.append(result)
        else:
            error_responses.append(result)

    # Calculate the amount of time the client should wait before sending in
    # more postings.

    wait_for = calc_wait_for_time(len(postings))

    # Queue the postings for later processing.

    if len(postings) > 0:
        tasks.process_postings.delay(postings)
        eventRecorder.record("POSTING_API", "POSTINGS_QUEUED",
                             len(postings), wait_for)

    # Finally, return the response back to the caller.

    response = {'error_responses' : error_responses,
                'wait_for'        : wait_for}

    return HttpResponse(json.dumps(response), mimetype="application/json")

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def calc_wait_for_time(num_postings_in_batch):
    """ Returns the number of seconds to wait before sending in more postings.

        'num_postings_in_batch' is the number of postings which were included
        in the current batch.

        The "wait_for" time is returned back to the caller, to regulate the
        pace at which postings are being sent in.

        We calculate the "wait_for" time based on the current size of the
        posting queue.
    """
    # Calculate the current size of the posting queue.

    num_postings_queued = \
        Event.objects.filter(type__type="POSTINGS_QUEUED").aggregate(
                Sum("primary_value"))['primary_value__sum']
    if num_postings_queued == None: num_postings_queued = 0

    num_postings_dequeued = \
        Event.objects.filter(type__type="POSTINGS_DEQUEUED").aggregate(
                Sum("primary_value"))['primary_value__sum']
    if num_postings_dequeued == None: num_postings_dequeued = 0

    posting_queue_size = num_postings_queued - num_postings_dequeued
    if posting_queue_size < 0: posting_queue_size = 0

    # Now calculate the "wait_for" time, based on the current size of the
    # posting queue.

    queue_koef = posting_queue_size / 1000
    if queue_koef > 2:
        wait_for = 2
    else:
        wait_for = queue_koef
    # wait_for = 1 * int()

    # Finally, return the calculated value back to the caller.

    return wait_for
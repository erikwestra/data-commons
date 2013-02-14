""" dataCommons.reporting.reports.postingQueueSize

    This module implements the "Posting Queue Size" report for the 3taps
    Reporting system.
"""
from django.db.models import *

from dataCommons.shared.lib import dateHelpers,reportHelpers

from dataCommons.monitoringAPI.models import *

#############################################################################

# The unique type code for this report:

type = "postingQueueSize"

#############################################################################

# A user-visible name for this report:

name = "Posting Queue Size"

#############################################################################

# A user-visible description for this report:

description = "This report shows the size of the posting queue over a " \
            + "given timeframe."

#############################################################################

# The list of parameters used by this report:

params = [{'name'     : "timeframe",
           'label'    : "View posting queue size for the last",
           'required' : True,
           'type'     : "timeframe",
           'default'  : "1h"},
]

#############################################################################

# The function to generate our report from a given set of parameters:

def generator(params, timezone_offset):

    startTime,endTime = reportHelpers.calc_timeframe(params['timeframe'])

    # Get the "POSTINGS_QUEUED" and "POSTINGS_DEQUEUED" event types.  We'll
    # need these for our various database queries.

    try:
        postings_queued_event = EventType.objects.get(type="POSTINGS_QUEUED")
    except EventType.DoesNotExist:
        postings_queued_event = None

    try:
        postings_dequeued_event = EventType.objects.get(
                                                    type="POSTINGS_DEQUEUED")
    except EventType.DoesNotExist:
        postings_dequeued_event = None

    # Now calculate the queue size at the start of the time period.  We get
    # this by summing up the total value of the POSTINGS_QUEUED events, and
    # then subtract the total value of the POSTINGS_DEQUEUED events, prior to
    # the starting time period.

    if postings_queued_event != None:
        query = Event.objects.filter(timestamp__lt=startTime,
                                     type=postings_queued_event)
        num_postings_added = \
            query.aggregate(Sum("primary_value"))['primary_value__sum']
        if num_postings_added == None: num_postings_added = 0
    else:
        num_postings_added = 0

    if postings_dequeued_event != None:
        query = Event.objects.filter(timestamp__lt=startTime,
                                     type=postings_dequeued_event)
        num_postings_removed = \
            query.aggregate(Sum("primary_value"))['primary_value__sum']
        if num_postings_removed == None: num_postings_removed = 0
    else:
        num_postings_removed = 0

    starting_queue_size = num_postings_added - num_postings_removed

    # Calculate the data to return to the caller.  Note that we use a data
    # reducer to simplify the data as necessary.

    reducer = reportHelpers.DataReducer()
    reducer.set_max_num_data_points(1000)
    reducer.set_period(startTime, endTime)
    reducer.set_value_combiner(sum)

    if postings_queued_event != None:
        for event in Event.objects.filter(timestamp__gte=startTime,
                                          timestamp__lte=endTime,
                                          type=postings_queued_event):
            reducer.add(event.timestamp, event.primary_value)

    if postings_dequeued_event != None:
        for event in Event.objects.filter(timestamp__gte=startTime,
                                          timestamp__lte=endTime,
                                          type=postings_dequeued_event):
            reducer.add(event.timestamp, -event.primary_value)

    reduced_data = reducer.get_reduced_data()

    # We now have a (possibly reduced) list of the changes to the queue size
    # for the desired time period.  Use these calculated values to build a
    # running total of the queue size over the time period.

    results = {'startTime' : reportHelpers.datetime_to_seconds(startTime,
                                                               timezone_offset),
               'endTime'   : reportHelpers.datetime_to_seconds(endTime,
                                                               timezone_offset),
               'periods'   : []}

    running_total = starting_queue_size

    for period_start,period_end,period_total in reduced_data:
        running_total = running_total + period_total
        timestamp = reportHelpers.datetime_to_seconds(period_start,
                                                      timezone_offset)
        results['periods'].append((timestamp, running_total))

    # Finally, return the calculated data back to the caller.

    return (True, results)

#############################################################################

# The Javascript function to render the generated report into the web page:

renderer = """
    function render(data) {
        var points = [];
        for (var i=0; i < data.periods.length; i++) {
            var row = data.periods[i];
            var timestamp = row[0];
            var queue_size = row[1];
            points.push([timestamp * 1000, queue_size]);
        }

        $.plot($("#report"), [
                    {data: points}
               ],
               {xaxis: {mode: "time",
                        axisLabel: "Time of Day",
                        min: data.startTime * 1000,
                        max: data.endTime * 1000},
                yaxis: {axisLabel: "Size of Posting Queue"}});
    }
"""


""" dataCommons.reporting.reports.processingTimes

    This module implements the "Processing Times" report for the 3taps
    Reporting system.
"""
from django.db.models import *

from dataCommons.shared.lib import dateHelpers,reportHelpers

from dataCommons.monitoringAPI.models import *

#############################################################################

# The unique type code for this report:

type = "processingTimes"

#############################################################################

# A user-visible name for this report:

name = "Processing Times"

#############################################################################

# A user-visible description for this report:

description = "This report shows how long it took to process each batch of " \
            + "postings as they come in from the grabbers."

#############################################################################

# The list of parameters used by this report:

params = [{'name'     : "timeframe",
           'label'    : "View processing times for the last",
           'required' : True,
           'type'     : "timeframe",
           'default'  : "1h"},
]

#############################################################################

# The function to generate our report from a given set of parameters:

def generator(params, timezone_offset):

    startTime,endTime = reportHelpers.calc_timeframe(params['timeframe'])

    # Get the "POSTINGS_PROCESSED" event type.  We'll need this for our various
    # database queries.

    try:
        postings_processed_event = EventType.objects.get(
                                                     type="POSTINGS_PROCESSED")
    except EventType.DoesNotExist:
        postings_processed_event = None

    # Now scan through the desired time period, grabbing all the
    # "POSTINGS_PROCESSED" events and passing them through a data reducer to
    # keep the number of data points reasonable.

    reducer = reportHelpers.DataReducer()
    reducer.set_max_num_data_points(1000)
    reducer.set_period(startTime, endTime)
    reducer.set_value_combiner(max)

    if postings_processed_event != None:
        for event in Event.objects.filter(timestamp__gte=startTime,
                                          timestamp__lte=endTime,
                                          type=postings_processed_event):
            num_postings = event.primary_value
            tot_time     = event.secondary_value # milliseconds.
            time_per_posting = tot_time / num_postings
            reducer.add(event.timestamp, time_per_posting)

    reduced_data = reducer.get_reduced_data()

    # Finally, collate the results and return them back to the caller.

    results = {'startTime' : reportHelpers.datetime_to_seconds(startTime,
                                                               timezone_offset),
               'endTime'   : reportHelpers.datetime_to_seconds(endTime,
                                                               timezone_offset),
               'periods'   : [] # List of (timestamp, time_per_posting) values.
              }

    for period_start,period_end,max_time_per_posting in reduced_data:
        timestamp = reportHelpers.datetime_to_seconds(period_start,
                                                      timezone_offset)
        results['periods'].append((timestamp, max_time_per_posting))

    return (True, results)

#############################################################################

# The Javascript function to render the generated report into the web page:

renderer = """
    function render(data) {
        var points = [];
        for (var i=0; i < data.periods.length; i++) {
            var row = data.periods[i];
            var timestamp = row[0];
            var time_per_posting = row[1];
            points.push([timestamp * 1000, time_per_posting]);
        }

        $.plot($("#report"), [
            {data: points,
             bars: {show:true}
            }
        ], {xaxis: {mode: "time",
                    axisLabel: "Time of Day",
                    min: data.startTime * 1000,
                    max: data.endTime * 1000},
            yaxis: {axisLabel: "Average Processing Time (ms)"}});
    }
"""


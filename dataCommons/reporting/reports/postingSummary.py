""" dataCommons.reporting.reports.postingSumamry

    This module implements the "Posting Summary" report for the 3taps
    Reporting system.
"""
import datetime

from django.db.models import *

from dataCommons.shared.lib import dateHelpers,reportHelpers

from dataCommons.shared.models import *

#############################################################################

# The unique type code for this report:

type = "postingSummary"

#############################################################################

# A user-visible name for this report:

name = "Posting Summary"

#############################################################################

# A user-visible description for this report:

description = "This report shows the number of postings in the database " \
            + "over a given date/time range."

#############################################################################

# The list of parameters used by this report:

params = [{'name'     : "timeframe",
           'label'    : "View a summary of postings for the last",
           'required' : True,
           'type'     : "timeframe",
           'default'  : "24h"},

          {'name'     : "chunk_size",
           'label'    : "Show the number of postings per",
           'required' : True,
           'type'     : "string",
           'choices'  : [("minute", "m"),
                         ("hour",   "h"),
                         ("day",    "d")],
           'default'  : "h"},

          {'name'     : "date_choice",
           'label'    : "Use the date/time when the posting was",
           'required' : True,
           'type'     : "string",
           'choices'  : [("added to the source system", "source"),
                         ("added to the 3taps database", "3taps")],
           'default'  : "3taps"},
]

#############################################################################

# The function to generate our report from a given set of parameters:

def generator(params, timezone_offset):

    # Process our parameters.

    startTime,endTime = reportHelpers.calc_timeframe(params['timeframe'])

    if params['chunk_size'] == "m":
        chunk_size = datetime.timedelta(minutes=1)
    elif params['chunk_size'] == "h":
        chunk_size = datetime.timedelta(hours=1)
    elif params['chunk_size'] == "d":
        chunk_size = datetime.timedelta(days=1)
    else:
        return (False,
                "Unknown chunk_size value: " + repr(params['chunk_size']))

    if params['date_choice'] == "source":
        date_field = "timestamp"
    elif params['date_choice'] == "3taps":
        date_field = "inserted"
    else:
        return (False,
                "Unknown date_choice value: " + repr(params['date_choice']))

    # Build a list of the time periods within the desired timeframe.

    periods = []
    period_start = startTime
    while period_start <= endTime:
        periods.append({'start' : period_start,
                        'end'   : period_start + chunk_size -
                                  datetime.timedelta(microseconds=1)})
        period_start = period_start + chunk_size

    # Calculate the total for each time period in turn.

    for period in periods:
        query = {date_field + "__gte" : period['start'],
                 date_field + "__lte" : period['end']}
        period['num_postings'] = Posting.objects.filter(**query).count()

    # Assemble the results to display.

    results = [] # List of (period_start, num_postings) tuples.

    for period in periods:
        timestamp = reportHelpers.datetime_to_seconds(period['start'],
                                                      timezone_offset)
        results.append((timestamp, period['num_postings']))

    # Finally, return the results back to the caller.

    return (True, results)

#############################################################################

# The Javascript function to render the generated report into the web page:

renderer = """
    function render(data) {
        var points = [];
        for (var i=0; i < data.length; i++) {
            var row = data[i];
            var timestamp = row[0];
            var queue_size = row[1];
            points.push([timestamp * 1000, queue_size]);
        }

        $.plot($("#report"), [
                    {data: points,
                     bars: {show:true}
                    }
               ],
               {xaxis: {mode : "time",
                        axisLabel: "Time of Day"},
                yaxis: {axisLabel: "Number of Postings"}});
    }
"""


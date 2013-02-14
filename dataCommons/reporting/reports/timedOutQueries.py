""" dataCommons.reporting.reports.timedOutQueries

    This module implements the "Timed Out Queries" report for the 3taps
    Reporting system.
"""
from django.db.models import *

from dataCommons.shared.lib import dateHelpers,reportHelpers

from dataCommons.monitoringAPI.models import *

#############################################################################

# The unique type code for this report:

type = "timedOutQueries"

#############################################################################

# A user-visible name for this report:

name = "Timed Out Queries"

#############################################################################

# A user-visible description for this report:

description = "This report displays a list of SQL queries that timed out."

#############################################################################

# The list of parameters used by this report:

params = [{'name'     : "timeframe",
           'label'    : "View timed out queries for the last",
           'required' : True,
           'type'     : "timeframe",
           'default'  : "1h"},
]

#############################################################################

# The function to generate our report from a given set of parameters:

def generator(params, timezone_offset):

    startTime,endTime = reportHelpers.calc_timeframe(params['timeframe'])

    # Get the "QUERY TIMED OUT" event type.  We'll need this for our various
    # database queries.

    try:
        query_timed_out_event = EventType.objects.get(type="QUERY_TIMED_OUT")
    except EventType.DoesNotExist:
        query_timed_out_event = None

    # Now scan through the desired time period, grabbing all the
    # "QUERY TIMED OUT" events.

    results = [] # List of (timestamp, sql) tuples.

    if query_timed_out_event != None:
        for event in Event.objects.filter(timestamp__gte=startTime,
                                          timestamp__lte=endTime,
                                          type=query_timed_out_event):
            timestamp = reportHelpers.datetime_to_seconds(event.timestamp)
#                                                          timezone_offset)
            results.append((timestamp, event.text))

    # Finally, return the list of timed-out queries back to the caller.

    return (True, results)

#############################################################################

# The Javascript function to render the generated report into the web page:

renderer = """
    function format_timestamp(timestamp) {
        var d = new Date(timestamp * 1000); // Convert seconds to ms.

        var month_names = new Array("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                    "Jul", "Aug", "Sept", "Oct", "Nov", "Dec");

        var date_string = d.getDate() + "-"
                        + month_names[d.getMonth()] + "-"
                        + d.getFullYear();

        var hours = d.getHours();
        if (hours.length == 1) {
            hours = "0" + hours;
        }

        var minutes = d.getMinutes();
        if (minutes.length == 1) {
            minutes = "0" + minutes;
        }

        var seconds = d.getSeconds();
        if (seconds.length == 1) {
            seconds = "0" + seconds;
        }

        var time_string = hours + ":" + minutes + ":" + seconds;

        return date_string + " " + time_string;
    }

    function render(data) {
        var table = $('<table cellspacing="0" cellpadding="5" border="1" ' +
                      ' width="100%"></table>');

        for (i=0; i < data.length; i++) {
            var row = data[i];

            var timestamp = row[0];
            var sql       = row[1];

            var tr = $('<tr></tr>');

            var td = $('<td nowrap></td>');
            td.css("font-size", "small");
            td.text(format_timestamp(timestamp));

            tr.append(td);

            var td = $('<td></td>');
            td.css("font-size", "small");
            td.text(sql);

            tr.append(td);
            table.append(tr);
        }

        var summary = $('<div></div>');
        summary.css("font-weight", "bold");
        summary.css("font-size", "small");
        summary.css("margin", "20px");
        summary.text(data.length + " timed out queries found");

        $("#report").css("width", "100%");
        $("#report").empty();
        $("#report").append(table);
        $("#report").append(summary);
    }
"""


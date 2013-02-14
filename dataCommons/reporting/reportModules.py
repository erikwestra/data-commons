""" dataCommons.reporting.reportModules

    This module provides a master list of all known report definition modules.

    When you create a new type of report, add an "import" statement to import
    the report definition module into this module, and then add it to the
    REPORT_MODULES global variable.  Note that the reports will be displayed in
    the UI in the order in which they are added to the REPORT_MODULES list.
"""
from dataCommons.reporting.reports import postingQueueSize
from dataCommons.reporting.reports import postingSummary
from dataCommons.reporting.reports import processingTimes
from dataCommons.reporting.reports import searchRequestTimes
from dataCommons.reporting.reports import summaryRequestTimes
from dataCommons.reporting.reports import timedOutQueries

#############################################################################

REPORT_MODULES = [
    postingQueueSize,
    postingSummary,
    processingTimes,
    searchRequestTimes,
    summaryRequestTimes,
    timedOutQueries,
]

""" dataCommons.shared.lib.eventRecorder

    This module allows various parts of the 3taps data commons system to record
    events as they occur.  The events are either passed on to the
    locally-installed Monitoring API, or sent to a remote server for
    processing.
"""
from django.conf import settings

#############################################################################

def record(source, type, primary_value=None, secondary_value=None, text=None):
    """ Record the occurrence of an event.

        The parameters are as follows:

            'source'

                A string indicating the source of this event.

            'type'

                A string indicating the type of event.

            'primary_value'

                An integer giving the primary value for this event, if any.

            'secondary_value'

                An integer giving the secondary value for this event, if any.

            'text'

                Some text to associate with this event, if any.

        If the Monitoring API is installed on this computer, we call the
        monitoring API directly to do the work.  Otherwise, we send off an HTTP
        request to the monitoring API machine to record the event remotely.

        If an error occurred, we raise a suitable RuntimeError so that the
        caller will know that something went wrong.
    """
    if "dataCommons.monitoringAPI" in settings.INSTALLED_APPS:
        # The monitoring API is directly available -> call it.
        from dataCommons.monitoringAPI import event_recorder
        err_msg = event_recorder.record(source, type,
                                        primary_value, secondary_value, text)
        if err_msg != None:
            raise RuntimeError(err_msg)
    else:
        # The monitoring API is on another computer -> send off an HTTP
        # request.
        raise RuntimeError("Remote event reporting is not implemented yet")


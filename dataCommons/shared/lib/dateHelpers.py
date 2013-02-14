""" dataCommons.shared.lib.dateHelpers

    This module defines various helper functions for dealing with date/time
    values.
"""
import datetime

from django.utils.timezone import utc

#############################################################################

def datetime_in_utc(secs=None):
    """ Return a datetime.datetime object with the given date and time in UTC.

        If supplied, 'secs' should be the number of seconds since the 1st of
        January, 1970 (a "unix time" value).

        We create and return a datetime.datetime object, in UTC, with the given
        date and time value.  If 'secs' is not supplied, we default to the
        current date and time in UTC.

        Note that the returned object will be timezone aware, as required by
        Django, and be accurate to the nearest second.

        If an error occurs, we return None.
    """
    if secs != None:
        try:
            value = datetime.datetime.utcfromtimestamp(secs)
        except ValueError:
            return None
    else:
        value = datetime.datetime.utcnow()

    return value.replace(tzinfo=utc, microsecond=0)

#############################################################################

def datetime_to_seconds(timestamp):
    """ Convert a datetime.datetime object to a unix time value in seconds.

        'timestamp' should be a datetime.datetime object representing a
        date/time value, in UTC.

        We return the number of seconds that have elapsed between the 1st of
        January 1970 and the given timestamp.  This is the "unix time"
        equivalent for the given date/time object.
    """
    delta = timestamp - datetime.datetime(1970, 1, 1).replace(tzinfo=utc)
    return (delta.days*24*3600) + delta.seconds

#############################################################################

def split_period(period):
    """ Split a time period code into its component parts.

        'period' should be a string consisting of a number followed by a
        letter, where the letter indicates the size of the time period and the
        number indicates the number of time periods.  For example, "7m" = 7
        minutes, while "14d" = 14 days.

        We return a (num_periods, period_size) tuple, where 'num_periods' is an
        integer and 'period_size' is a string.  If the period cannot be split,
        we return (None, None).
    """
    s1 = ""
    s2 = ""
    for i,char in enumerate(period):
        if not char.isdigit():
            s1 = period[:i]
            s2 = period[i:]
            break

    if (s1 == "") or (s2 == ""):
        return (None, None)

    try:
        num_periods = int(s1)
    except ValueError:
        return (None, None)

    period_size = s2.lower()

    return (num_periods, period_size)

#############################################################################

def parse_period(period):
    """ Attempt to parse the give time period string.

        'period' should be a string consisting of a number followed by a
        letter, where the letter indicates the size of the time period and the
        number indicates the number of time periods.  For example, "7m" = 7
        minutes, while "14d" = 14 days.

        The following time period codes are supported:

            s = seconds
            m = minutes
            h = hours
            d = days
            w = weeks

        Upon completion, we return a (success, value) tuple, where 'success' is
        True if and only if the given string could be parsed as a time period.
        If success is True, 'value' will be a datetime.timedelta object
        representing the parsed time period.  Otherwise, 'value' will be a
        string describing why the time period wasn't accepted.
    """
    num_periods,period_size = split_period(period)

    if period_size == "s":
        return (True, datetime.timedelta(seconds=num_periods))
    elif period_size == "m":
        return (True, datetime.timedelta(minutes=num_periods))
    elif period_size == "h":
        return (True, datetime.timedelta(hours=num_periods))
    elif period_size == "d":
        return (True, datetime.timedelta(days=num_periods))
    elif period_size == "w":
        return (True, datetime.timedelta(weeks=num_periods))
    else:
        return (False, "Invalid time period: " + repr(period))

#############################################################################

def parse_timestamp(timestamp):
    """ Attempt to parse the given timestamp string.

        'timestamp' should be a string in "YYYYMMDDHHMMSS" format, in UTC.

        Upon completion, we return a (success, value) tuple, where 'success' is
        True if and only if the given string could be parsed as a timestamp.
        If success is True, 'value' will be a datetime.datetime object holding
        the parsed date/time value.  Otherwise, 'value' will be a string
        describing why the time period wasn't accepted.
    """
    try:
        parsed_timestamp = datetime.datetime.strptime(timestamp,
                                                      "%Y%m%d%H%M%S")
    except ValueError:
        return (False, "Invalid timestamp: " + repr(timestamp))

    return (True, parsed_timestamp)

#############################################################################

def calc_date_range(start_datetime, end_datetime, timedelta):
    """ Calculate and return a date range based on incomplete parameters.

        The parameters are as follows:

            'start_datetime'

                A datetime.datetime object representing the desired starting
                date/time, or None if no starting date/time was supplied.

            'end_datetime'

                A datetime.datetime object representing the desired ending
                date/time, or None if no ending date/time was supplied.

            'timedelta'

                A datetime.timedelta object, as returned by a previous call to
                parse_period(), above, representing the desired time period, or
                None if no time period was specified.

        We calculate the desired date range in the following way:

            1. If both 'start_datetime' and 'end_datetime' are supplied, we
               return these directly and ignore the timedelta parameters.

            2. If 'start_datetime' is supplied but 'end_datetime' is not, we
               calculate the end date/time value as the starting value plus the
               requested timedelta.

            3. If 'start_datetime' is not supplied but 'end_datetime' is, we
               calculate the start date/time value as the ending value minus
               the requested timedelta.

            4. If neither the 'start_datetime' nor the 'end_datetime' values
               are supplied, we calculate the ending date/time as the current
               date and time, and the starting date/time as the ending value
               minus the requested timedelta.

        Upon completion, we return a (start_datetime, end_datetime) tuple,
        where both values are datetime.datetime objects representing the
        desired date/time range, in UTC.
    """
    if start_datetime != None and end_datetime != None:
        return (start_datetime, end_datetime)
    elif start_datetime == None and end_datetime != None:
        return (end_datetime - timedelta, end_datetime)
    elif start_datetime != None and end_datetime == None:
        return (start_datetime, start_datetime + timedelta)
    else:
        now = datetime_in_utc()
        return (now - timedelta, now)

#############################################################################

def calc_period_label(timestamp, period_size):
    """ Label a timestamp for display within a period of the given size.

        'timestamp' is a datetime.datetime object representing a point in time,
        and 'period_size' is a letter representing the size of a time period,
        as returned by a previous call to split_period(), above.

        We take the given point in time, and convert it to a string for display
        in a format which makes sense for the given period.  For example the
        timestamp 7/Jan/2013 12:34:56 PM would be displayed as:

            12:34:56   for a period_size of "s".
            12:34      for a period_size of "m"
            12:00      for a period_size of "h"
            7/Jan      for a period_size of "d"
            7/Jan      for a period_size of "w"
    """
    if period_size == "s":
        return timestamp.strftime("%H:%M:%s")
    elif period_size == "m":
        return timestamp.strftime("%H:%M")
    elif period_size == "h":
        return timestamp.replace(minutes=0).strftime("%H:%M")
    elif period_size == "d":
        return timestamp.strftime("%d/%b")
    elif period_size == "w":
        return timestamp.strftime("%d/%b")


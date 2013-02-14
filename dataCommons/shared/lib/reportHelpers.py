""" dataCommons.shared.lib.reportHelpers

    This module defines various helper functions useful for generating reports.
"""
import datetime
import math
import time

from django.utils.timezone import utc

from dataCommons.shared.lib import dateHelpers

#############################################################################

# The following constants make it easier to add and subtract time values.

ONE_MICROSECOND = datetime.timedelta(microseconds=1)
ONE_SECOND      = datetime.timedelta(seconds=1)
ONE_MINUTE      = datetime.timedelta(minutes=1)
ONE_HOUR        = datetime.timedelta(hours=1)
ONE_DAY         = datetime.timedelta(days=1)
ONE_WEEK        = datetime.timedelta(weeks=1)

#############################################################################

DISABLE_DATA_REDUCER = False # Set to True for testing.

#############################################################################

class InvalidTimeframe(Exception):
    """ An exception raised when an invalid timeframe value was supplied.
    """
    def __init__(self, message):
        """ Standard initialiser.
        """
        self.message = message

#############################################################################

def datetime_to_seconds(timestamp, timezone_offset=None):
    """ Convert a datetime.datetime object to a unix time value in seconds.

        The parameters are as follows:

            'timestamp'

                A datetime.datetime object representing a date/time value, in
                UTC.

            'timezone_offset'

                The caller's timezone offset, if any.

        If a timezone offset was supplied, we convert the date/time value from
        UTC into the caller's timezone.

        Upon completion, we return the number of seconds that have elapsed
        between the 1st of January 1970 and the given timestamp.  This is the
        "unix time" equivalent for the given date/time object.
    """
    seconds = dateHelpers.datetime_to_seconds(timestamp)
    if timezone_offset != None:
        seconds = seconds - (timezone_offset * 60)
    return seconds

#############################################################################

def calc_timeframe(timeframe):
    """ Calculate the starting and ending timestamp for a given timeframe.

        'timeframe' is a string encoding a timeframe value; we return a
        (start_time, end_time) tuple, where 'start_time' and 'end_time' are
        both datetime.datetime objects, in UTC.

        If the timeframe could not be parsed (for example because the period
        code was invalid, or the ending time is greater than the starting
        time), a suitable InvalidTimeframe exception will be raised.
    """
    # Start by splitting the timeframe string at the two ".." characters, if
    # they exist.

    if ".." in timeframe:
        num_parts   = 2
        part1,part2 = timeframe.split("..", 1)
    else:
        num_parts = 1

    # The following helper function parses a part of the timeframe string.  It
    # returns a (type,value) tuple, where 'type' is "period", "timestamp" or
    # "unknown", and 'value' is a datetime.timedelta object, a
    # datetime.datetime object, or None.

    def parse_part(s):
        success,results = dateHelpers.parse_period(s)
        if success:
            return ("period", results)
        else:
            success,results = dateHelpers.parse_timestamp(s)
            if success:
                return ("timestamp", results)
            else:
                return ("unknown", None)

    # The following helper function calculates the starting and ending
    # date/time values for given time period size.  It returns a (period_start,
    # period_end) tuple, where 'period_start' is the start of the current time
    # period, and 'period_end' is the end of that period.  For example, if
    # 'period_size' is "d" (days), then 'period_start' will be the start of
    # the current day, and 'period_end' will be the end of the current day.
    #
    # Note that the returned time period is accurate to the nearest
    # microsecond.

    def calc_current_period(period_size):

        now = dateHelpers.datetime_in_utc()

        if period_size == "s":
            period_start = now.replace(microsecond=0)
            period_end   = period_start + ONE_SECOND - ONE_MICROSECOND
        elif period_size == "m":
            period_start = now.replace(second=0, microsecond=0)
            period_end   = period_start + ONE_MINUTE - ONE_MICROSECOND
        elif period_size == "h":
            period_start = now.replace(minute=0, second=0, microsecond=0)
            period_end   = period_start + ONE_HOUR - ONE_MICROSECOND
        elif period_size == "d":
            period_start = now.replace(hour=0, minute=0, second=0,
                                       microsecond=0)
            period_end   = period_start + ONE_DAY - ONE_MICROSECOND
        elif period_size == "w":
            period_start = now.replace(hour=0, minute=0, second=0,
                                       microsecond=0)
            while period_start.weekday() > 0:
                period_start = period_start - ONE_DAY
            period_end = period_start + ONE_WEEK - ONE_MICROSECOND
        else:
            raise RuntimeError("Invalid time period: " + repr(period))

        return (period_start, period_end)

    # Parse each part of the timeframe string.

    if num_parts == 1:
        type,value = parse_part(timeframe)
        if type != "period":
            raise InvalidTimeframe("Invalid timeframe: " + repr(timeframe))

        num_periods,period_size = dateHelpers.split_period(timeframe)
        period_start,period_end = calc_current_period(period_size)

        for i in range(num_periods-1):
            if period_size == "s":
                period_start = period_start - ONE_SECOND
            elif period_size == "m":
                period_start = period_start - ONE_MINUTE
            elif period_size == "h":
                period_start = period_start - ONE_HOUR
            elif period_size == "d":
                period_start = period_start - ONE_DAY
            elif period_size == "w":
                period_start = period_start - ONE_WEEK

        return (period_start, period_end)
    elif num_parts == 2:
        type1,value1 = parse_part(part1)
        type2,value2 = parse_part(part2)

        if type1 == "period" and type2 == "timestamp":
            start_datetime = None
            end_datetime   = value2
            timedelta      = value1
        elif type1 == "timestamp" and type2 == "period":
            start_datetime = value1
            end_datetime   = None
            timedelta      = value2
        elif type1 == "timestamp" and type2 == "timestamp":
            start_datetime = value1
            end_datetime   = value2
            timedelta      = None
        else:
            raise InvalidTimeframe("Invalid timeframe: " + repr(timeframe))
    else:
        raise InvalidTimeframe("Unable to parse timeframe: " + repr(timeframe))

    # Calculate the desired date range.

    start_datetime,end_datetime = dateHelpers.calc_date_range(start_datetime,
                                                              end_datetime,
                                                              timedelta)

    # Make sure the entered range makes sense.

    if start_datetime > end_datetime:
        raise InvalidTimeframe("Invalid timeframe: " + repr(timeframe))

    # Finally, return the calculated date range back to the caller

    return (start_datetime, end_datetime)

#############################################################################

class DataReducer:
    """ Helper class to reduce the number of data points in a time-based chart.

        The DataReducer works by mapping time-based values (truncated to the
        nearest second) into "buckets".  If the total timeframe for a report is
        small enough, each bucket corresponds to a single second.  Otherwise,
        the bucket size is increased to keep the total number of data points to
        a given limit.
    """
    def __init__(self):
        """ Standard initialiser.
        """
        self._max_num_data_points = 1000
        self._value_combiner      = sum
        self._start_time          = None
        self._end_time            = None
        self._is_setup            = False
        self._seconds_to_bucket   = {} # Maps int unix time to _buckets index.
        self._buckets             = []

        if DISABLE_DATA_REDUCER:
            self._data = [] # For testing.


    def set_max_num_data_points(self, max_num_data_points):
        """ Set the maximum number of data points to include in the report.

            If you do not set the maximum number of data points, the data
            reducer will default to 1,000.
        """
        self._max_num_data_points = max_num_data_points


    def set_period(self, start_time, end_time):
        """ Set the period covered by this report.

            'start_time' and 'end_time' are datetime.datetime objects
            corresponding to the start and end of the time-based report.

            Note that this must be called before any data points are added to
            the data reducer.
        """
        self._start_time = start_time
        self._end_time   = end_time


    def set_value_combiner(self, value_combiner):
        """ Set the function to use to combine two or more data points.

            'value_combiner' should be a Python callable object that takes a
            list of values and returns the value to use for the bucket that
            contains those values.  The following built-in functions can be
            used to perform simple data reductions:

                sum
                min
                max

            If you need a more sophisticated value reducer, simply define your
            own function and pass it instead.

            If you do not set an explicit value combiner, the data reducer will
            use the built-in sum() function.
        """
        self._value_combiner = value_combiner


    def add(self, timestamp, value):
        """ Add a data point to the report.

            'timestamp' should be a datetime.datetime object corresponding to a
            given point in time, and 'value' should be the value to associate
            with that point in time.

            We add the given data point to the report.
        """
        if DISABLE_DATA_REDUCER:
            self._data.append((timestamp, timestamp, value))
        else:
            if not self._is_setup:
                self._setup()
                self._is_setup = True

            seconds = datetime_to_seconds(timestamp)

            try:
                bucket_num = self._seconds_to_bucket[seconds]
            except KeyError:
                raise RuntimeError("timestamp outside report period!")

            self._buckets[bucket_num]['values'].append(value)


    def get_reduced_data(self):
        """ Return the reduced data derived from the supplied data points.

            We return a list of (start_time, end_time, value) tuples, where
            'start_time' and 'end_time' are datetime.datetime objects
            corresponding to the start and end of each time period, and 'value'
            is the combined value for that period.  Note that the returned list
            will have at most the number of data points defined by a previous
            call to set_max_num_data_points(), above, or 1000 if that method
            has not been called.
        """
        if DISABLE_DATA_REDUCER:
            self._data.sort()
            return self._data
        else:
            results = []
            for bucket in self._buckets:
                if len(bucket['values']) == 0:
                    continue # Skip empty buckets.
                elif len(bucket['values']) == 1:
                    results.append((bucket['start'],
                                    bucket['end'],
                                    bucket['values'][0]))
                else:
                    combined_value = self._value_combiner(bucket['values'])
                    results.append((bucket['start'],
                                    bucket['end'],
                                    combined_value))
            return results

    # =====================
    # == PRIVATE METHODS ==
    # =====================

    def _setup(self):
        """ Setup the data reducer.

            This is called the first time the add() method is called.  We set
            up the internal data structures used by the data reducer.

            Note that if something is wrong (eg, no time period was specified),
            we raise a suitable RuntimeError.
        """
        if self._start_time == None or self._end_time == None:
            raise RuntimeError("DataReducer.set_period() not called!")

        # Calculate the total number of seconds in the reporting time period.

        start_secs   = datetime_to_seconds(self._start_time)
        end_secs     = datetime_to_seconds(self._end_time)
        tot_num_secs = end_secs - start_secs + 1

        # Calculate how many buckets we need, and how many seconds are covered
        # by each bucket.

        num_buckets     = tot_num_secs # initially.
        secs_per_bucket = 1

        while num_buckets > self._max_num_data_points:
            secs_per_bucket = secs_per_bucket + 1
            num_buckets     = int(math.ceil(tot_num_secs / secs_per_bucket))

        # Setup the mapping from seconds to bucket indexes.

        for cur_secs in range(start_secs, end_secs+1):
            bucket_index = int(float(cur_secs-start_secs) /
                               float(secs_per_bucket))
            self._seconds_to_bucket[cur_secs] = bucket_index

        # Finally, setup the list of buckets.

        for bucket_num in range(num_buckets):
            bucket_start_secs = start_secs + bucket_num * secs_per_bucket
            bucket_end_secs   = bucket_start_secs + secs_per_bucket - 1

            bucket_start = dateHelpers.datetime_in_utc(bucket_start_secs)
            bucket_end   = dateHelpers.datetime_in_utc(bucket_end_secs)

            self._buckets.append({'start'  : bucket_start,
                                  'end'    : bucket_end,
                                  'values' : []})


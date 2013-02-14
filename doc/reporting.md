<center>
    <h1>
        The 3taps Data Commons
    </h1>
    <h3>
        Reporting Infrastructure
    </h3>
    <h4>
        Version 0.1
    </h4>
</center>

This document describes how the 3taps Data Commons Reporting application works.
The Reporting application uses the following URLs:

> `/reporting`
> 
> > The main entry point to the Reporting application.  Viewing this page will
> > display a list of the available types of reports.
> 
> `/reporting/<TYPE>`
> 
> > The page for generating and viewing a given type of report.  `<TYPE>` will
> > be the desired type of report.

The Reporting application makes use of __report definition modules__ to define
the various types of report, what parameters they accept, how they are
generated, and how they are displayed to the user.  The `/reports/<TYPE>` page
makes use of [JQuery][] and the [Flot][] Javascript libraries to actually
display the generated report.

  [JQuery]: http://jquery.com
  [Flot]: http://flotcharts.org

NOTE: The following plugins are currently supported for Flot:

 * jquery.flot.navigate
 * [flot-axislabels](https://github.com/markrcote/flot-axislabels)

More plugins will be added as they are needed.

-----------------------------------------------------------------------------

### Report Definition Modules ###

Each report type has a module in the `dataCommons/reporting/reports` directory
that contains all the information about that type of report.  Each report
definition module must contain the following top-level entries:

> __type__
> 
> > The unique string identifying this type of report.
> 
> __name__
> 
> > The user-visible name for this type of report.
> 
> __description__
> 
> > A user-visible description for this type of report.
> 
> __params__
> 
> > A list of parameter definitions for this type of report.  See below for
> > details.
> 
> __generator__
> 
> > A Python callable object that generates the raw data for a report.  This
> > callable object should accept two parameters:
> > 
> > > `params`
> > > 
> > > > A dictionary containing the parameters to use for generating this
> > > > report.  Each dictionary entry maps a parameter name to its associated
> > > > value.
> > > 
> > > `timezone_offset`
> > > 
> > > > The caller's timezone offset, if supplied.  This can be used to convert
> > > > UTC values into the caller's timezone, if this type of report uses
> > > > date/time values.
> > 
> > Upon completion, the report generator should return a `(success, result)`
> > tuple, where `success` is True if and only if the report was generated
> > successfully, and `result` is either the generated report data or a string
> > indicating why the report could not be generated.
> > 
> > Note that the returned data must be serializable by the JSON encoder.
> 
> __renderer__
> 
> > A string containing the Javascript code to use to display this report
> > within a web page.  This Javascript code should define a function named
> > `render` which takes a single parameter, the report data returned by the
> > generator function, and displays the contents of the report.  The renderer
> > function can make use of the Flot library as well as JQuery. The generated
> > report should be be placed inside a `<div>` element with the ID "report";
> > this `<div>` is defined by the surrounding web page.  For example, here is
> > a trivially simple report renderer:
> > 
> > >     function render(data) {
> > >       $("#report").html("hello world!");
> > >     }

-----------------------------------------------------------------------------

### Report Parameters ###

The __params__ entry in the report definition module lists the various
parameters supported by this type of report.  This will be a list of
parameters, where each list item is a dictionary with the following entries:

> __name__
> 
> > The internal name used for this parameter.  Must be unique for this type of
> > report.
> 
> __label__
> 
> > A user-visible label for this parameter.
> 
> __required__
> 
> > Is this parameter required?  If this is not supplied, the parameter will
> > not be required.
> 
> __type__
> 
> > The type of value which this parameter can contain.  The following
> > parameter types are currently supported:
> > 
> > > __string__
> > > 
> > > > A string value.
> > > 
> > > __integer__
> > > 
> > > > An integer value.
> > > 
> > > __float__
> > > 
> > > > A floating-point value.
> > > 
> > > __boolean__
> > > 
> > > > A boolean (true/false) value.
> > > 
> > > __timeframe__
> > > 
> > > > This special parameter type is used to represent the timeframe for a
> > > > time-based report.  Custom UI controls are used to let the user choose
> > > > the timeframe to use when generating the report.  A timeframe
> > > > parameter's value will be a specially-formatted string encapsulating
> > > > the desired timeframe.  Before we look at the format of this string, we
> > > > need to define a couple of terms:
> > > > 
> > > > * __PERIOD__ is a time period code.  Time period codes consist of a
> > > >   number followed by a letter, where the letter indicates the size of
> > > >   the time period and the number is the number of time periods.  For
> > > >   example, `7m` = 7 minutes and `14d` = 14 days.
> > > > 
> > > > > The following time period letters are currently supported:
> > > > > 
> > > > > > | __Letter__ |     | __Meaning__ |
> > > > > > | :--------: | :-: | :---------: |
> > > > > > | s          |     | Seconds     |
> > > > > > | m          |     | Minutes     |
> > > > > > | h          |     | Hours       |
> > > > > > | d          |     | Days        |
> > > > > > | w          |     | Weeks       |
> > > > 
> > > > * __YYYYMMDDHHMMSS__ is an explicit timestamp value.  For example,
> > > >   `20130109023800` means 2:38:00 AM on January the 9th, 2013.  Note
> > > >   that all timestamp values are given in UTC.
> > > > 
> > > > Using these two terms, we can encode a timeframe value as a string
> > > > using one of the following formats:
> > > > 
> > > > >     PERIOD
> > > > > 
> > > > > > Calculate the report timeframe based on the given time period code,
> > > > > > ending at the current point of time.  For example, a timeframe
> > > > > > value of `1w` corresponds to "the last week".
> > > > > 
> > > > >     YYYYMMDDHHMMSS..PERIOD
> > > > > 
> > > > > > Calculate the report's timeframe based on the given period of time,
> > > > > > starting at the given date and time.  For example, a timeframe
> > > > > > value of `20130109023800..1d` means "one day starting at 2:38:00 AM
> > > > > > on January the 9th, 2013.
> > > > > 
> > > > >     PERIOD..YYYYMMDDHHMMSS
> > > > > 
> > > > > > Calculate the report's timeframe based on the given period of time,
> > > > > > ending at the given date and time.  For example, a timeframe value
> > > > > > of `4h..20130109023800` means "four hours ending at 2:38:00 AM on
> > > > > > January the 9th, 2013.
> > > > > 
> > > > >     YYYYMMDDHHMMSS..YYYYMMDDHHMMSS
> > > > > 
> > > > > > Calculate the report's timeframe based on the two given timestamps.
> > > > > > For example, a timeframe value of `20130106000000..20130108000000`
> > > > > > means "all times between midnight on the 6th of January, 2013 and
> > > > > > midnight on the 8th of January, 2013".
> 
> __choices__
> 
> > If supplied, this gives a list of choices the user can choose between.
> > This should be a list of (label,value) tuples, where 'label' is the label
> > shown to the user, and 'value' is the associated value to use for this
> > parameter.  Note that this is only supported for __string__ and __integer__
> > parameter types.
> 
> __default__
> 
> > The default value to use for this parameter.  If this is not specified, the
> > parameter will be set to `None`.  Note that required parameters must have a
> > default value.

-----------------------------------------------------------------------------

### Defining New Types of Reports ###

Creating a new type of report involves two steps:

 1. Create a new report definition module in the
    `dataCommons/reporting/reports` directory.  Be sure to include all the
    top-level definitions listed above in your new module.

 2. Add an __import__ statement to the `dataCommons/reporting/reportModules.py`
    module, importing your new module.

 3. Modify the __REPORT_MODULES__ global in `reportModules.py` to include your
    new report definition module.  Note that you should enter your report into
    the list in a position where it will appear alphabetically by name.

-----------------------------------------------------------------------------

### Report Helpers ###

The `dataCommons.shared.lib.reportHelpers` module defines various helper
functions which make it easier to create report definition modules.  The
following helper functions are made available by this module:

>     datetime_to_seconds(timestamp, timezone_offset=None)
> 
> > Convert a datetime.datetime object to a unix time value in seconds.
> > 
> > The parameters are as follows:
> > 
> > > `timestamp`
> > > 
> > > > A datetime.datetime object representing a date/time value, in UTC.
> > > 
> > > `timezone_offset`
> > > 
> > > > The caller's timezone offset, if any.
> > > 
> > > If a timezone offset was supplied, we convert the date/time value from
> > > UTC into the caller's timezone.
> > > 
> > > Upon completion, we return the number of seconds that have elapsed
> > > between the 1st of January 1970 and the given timestamp.  This is the
> > > "unix time" equivalent for the given date/time object.
> > 
> > This can be used to convert `datetime` objects into a form where they can
> > be serialized and sent to the Javascript rendering function for display.
> > 
> > __NOTE:__ The value returned by this function is the number of _seconds_
> > that have elapsed since the 1st of January, 1970.  Javascript timestamp
> > values are measured as the number of _milliseconds_ since the 1st of
> > January 1970.  Thus, you typically have to multiply the returned number by
> > 1,000 to get the correct value when working with timestamps in Javascript.
> 
>     calc_timeframe(timeframe)
> 
> > Calculate the starting and ending timestamp for a given timeframe value.
> > `timeframe` should be a string encoding a timeframe value, as described
> > above.
> > 
> > This function parses the given timeframe, and returns a `(start_time,
> > end_time)` tuple, where `start_time` and `end_time` are datetime.datetime
> > values representing the calculated timeframe.
> > 
> > If the timeframe could not be parsed (for example because the period code
> > was invalid, or the ending time is greater than the starting time), a
> > suitable `dataCommons.shared.lib.reportHelpers.InvalidTimeframe` exception
> > will be raised.  Note that the report generator can simply call the
> > `calc_timeframe()` helper function and ignore these exceptions as they will
> > be caught and handled automatically by the reporting infrastructure.

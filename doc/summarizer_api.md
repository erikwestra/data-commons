<center>
    <h1>
        The 3taps Data Commons
    </h1>
    <h3>
        The Summarizer API
    </h3>
    <h4>
        Specification Version 0.2
    </h4>
</center>

The 3taps Summarizer API is responsible for calculating summaries of postings
across various dimensions.  For example, it can be used to calculate how many
matching postings come from each country, like this:

>     USA               12,376
>     United Kingdom    3,402
>     Australia         98
>     New Zealand       7

Note that the Summarizer API is closely related to the Search API; for a given
set of filters, the Summarizer API will return the number of matching postings,
while the Search API will return the postings themselves.


### Calling the 3taps Summarizer API ###

The Summarizer API is accessed via a single entry point, which can be found at
the following URL:

>     http://3taps.com/api/xxx/summarizer

where `xxx` is the version number of the Summarizer API that you wish to
access, or the special string `latest` to automatically access the most recent
version of the API.

The Summarizer API call is made using an HTTP `GET` request to the above URL.
The API call accepts the following parameters:

> `auth_token`
> 
> > This will eventually be the authentication token used to authenticate the
> > caller.  Note that this is currently ignored.
> 
> `dimension`
> 
> > A string indicating which dimension to calculate the summary across.  The
> > following values are currently supported:
> > 
> > > __category__  
> > > __location__  
> > > __source__  
> 
> `category_group`
> 
> > The 3taps category grouping code to filter the summary by.  Only postings
> > with the given category group will be included in the summary.
> 
> `category`
> 
> > The 3taps category code to filter the summary by.  Only postings with the
> > given category code will be included in the summary.
> 
> `country`
> 
> > The 3taps country code to filter the summary by.  Only postings with the
> > given country code will be included in the summary.
> 
> `state`
> 
> > The 3taps state to filter the summary by.  Only postings with the given
> > state code will be included in the summary.
> 
> `metro`
> 
> > The 3taps metro area code to filter the summary by.  Only postings with the
> > given metro area code will be included in the summary.
> 
> `region`
> 
> > The 3taps region code to filter the summary by.  Only postings with the
> > given region code will be included in the summary.
> 
> `county`
> 
> > The 3taps county code to filter the summary by.  Only postings with the
> > given county code will be included in the summary.
> 
> `city`
> 
> > The 3taps city code to filter the summary by.  Only postings with the given
> > city code will be included in the summary.
> 
> `locality`
> 
> > The 3taps locality code to filter the summary by.  Only postings with the
> > given locality code will be included in the summary.
> 
> `zipcode`
> 
> > The 3taps ZIP code to filter the summary by.  Only postings with the given
> > ZIP code will be included in the summary.
> 
> `source`
> 
> > The 3taps source code to filter the summary by.  Only postings with the
> > given source code will be included in the summary.
> 
> `heading`
> 
> > A freeform text string to filter the summary by.  Only postings with the
> > given string in their heading wil be included in the summary.
> 
> `body`
> 
> > A freeform text string to filter the summary by.  Only postings with the
> > given string in their body will be included in the summary.
> 
> `text`
> 
> > A freeform text string to filter the summary by.  Only postings with the
> > given string in their heading or body will be included in the summary.
> 
> `timestamp`
> 
> > This parameter is used to only include postings with a given range of
> > timestamp values.  The parameter's value should be a string of the form:
> > 
> > >     MIN_TIMESTAMP..MAX_TIMESTAMP
> > 
> > where `MIN_TIMESTAMP` and `MAX_TIMESTAMP` represent the minimum and maximum
> > timestamp values, respectively.  Both timestamps should be an integer
> > number of seconds since the 1st of January 1970 ("unix time"), in UTC.
> 
> `price`
> 
> > This parameter is used to only include postings with a given range of price
> > values.  The parameter's value should be a string formatted in one of the
> > following ways:
> > 
> > >     MIN_PRICE..MAX_PRICE
> > >     MIN_PRICE..
> > >     ..MAX_PRICE
> > 
> > `MIN_PRICE` and `MAX_PRICE` represent the minimum and maximum price values.
> > If both are supplied, then only postings with the given range of price
> > values will be included in the summary.  If only a minimum price is
> > supplied, only postings greater than or equal to that minimum price will be
> > included.  Similarly, if only a maximum price is supplied, only postings
> > less than or equal to that maximum price will be included.
> > 
> > Note that price values can be given as either integer or floating-point
> > values.
> 
> `currency`
> 
> > Only include postings in the given currency.  The parameter's value should
> > be a 3-character ISO-4217 currency code.
> 
> `annotations`
> 
> > One or more annotation values to filter the summary by.  The value of this
> > parameter should consist of one or more `key:value` pairs separated by
> > either `AND` or `OR`, and the whole string surrounded by `{` and `}`
> > characters.  For example:
> > 
> > >     annotations={make:ford AND model:mustang}
> > 
> > Note that the AND terms are interpreted ahead of the OR terms.  To adjust
> > the order in which the terms are interpreted, you should use parentheses
> > like this:
> > 
> > >     annotations={make:ford AND (model:mustang OR model:fairmont)}
> > 
> > __Note:__ annotation-based filtering will not be supported initially.
> 
> `status`
> 
> > The status value to filter the summary by.  The following status values are
> > currently supported:
> > 
> > >     offered
> > >     wanted
> > >     lost
> > >     stolen
> > >     found
> > >     deleted
> 
> `has_image`
> 
> > If this parameter is supplied and has the value "1", only postings which
> > have an image will be included in the summary.  If this parameter has the
> > value "0", only postings which do not have images will be included in the
> > summary.
> 
> `include_deleted`
> 
> > By default, deleted postings will not be included in the summary.  If this
> > parameter is supplied and has the value "1", however, deleted postings will
> > be included in the calculated summary.

Upon completion, the API call will return an HTTP status code of 200 (OK), a
Content-Type of `application/json`, and the body of the response will be a
JSON-encoded object with the following fields:

> `success`
> 
> > A boolean indicating whether or not the summary request succeeded.
> 
> `error`
> 
> > If the summary request was not successfully processed, this will be a string
> > describing what went wrong.
> 
> `summary`
> 
> > An array-of-arrays which holds the calculated summary, like this:
> > 
> > >     [["country", "USA", 12376],
> > >      ["country", "GBR", 3402],
> > >      ["country", "AUS", 98],
> > >      ["country", "NZL", 7]]
> > 
> > Each summary item will be represented by an array with the following three
> > entries:
> > 
> > > 1. The type of summary item.  This will be one of the following:
> > > 
> > > >     `category_group`  
> > > >     `category`  
> > > >     `country`  
> > > >     `state`  
> > > >     `metro`  
> > > >     `region`  
> > > >     `county`  
> > > >     `city`  
> > > >     `locality`  
> > > >     `zipcode`  
> > > >     `source`  
> > > 
> > > 2. The 3taps code for the summary item.  For example, if the type is `region`,
> > >    then this value will be the 3taps region code for this summary item.
> > > 
> > > 3. The number of matching postings.


### Understanding the Summarizer API ###

The summary returned by the Summarizer API will vary depending on the
parameters you have supplied.  At the simplest level (ie, with no filter
parameters supplied), a `category` summary will return the number of postings
within each of the top-level category groups.  Similarly, a `location` summary
will return the number of postings within each country, and a `source` summary
will return the number of postings submitted by each data source.

As filters are supplied, they not only constrain the results to only include
postings which match that filter value, they can also be used to "drill down"
to more detailed summaries.  For example, if you supply a `category_group`
filter for a category summary, the returned summary will list the various
categories within that group.  Similarly, you can drill down through the
various location levels by specifying a `country`, `state`, `metro`, `region`,
`county`, `city`, `locality` or `zipcode` parameter.

<center>
    <h1>
        The 3taps Data Commons
    </h1>
    <h3>
        The Posting API
    </h3>
    <h4>
        Specification Version 0.3
    </h4>
</center>

The 3taps Posting API is responsible for receiving incoming postings from
external data sources.  These postings are then added to the 3taps posting
database so they can be searched against, and are also sent to outgoing
notification streams.


### Accessing the 3taps Posting API ###

The Posting API is accessed via the following URL:

>     http://3taps.com/api/xxx/posting

where `xxx` is the version number of the Posting API that you wish to access,
or the special string `latest` to automatically access the most recent version
of the API.


### The Posting Object ###

The 3taps Posting API makes use of __posting objects__ to represent a single
posting.  These are JSON-formatted objects with the following fields:

> `account_id`
> 
> > A string identifying the user who submitted the posting.  Note that this is
> > currently not linked to an identity in the 3taps Identity API.
> 
> `source` _(required)_
> 
> > A string identifying the source system where the posting originated from.
> 
> `category` _(required)_
> 
> > The 3taps category code to associate with this posting.
> 
> `location`
> 
> > An object representing this posting's location.  The location object can
> > have any of the following fields:
> > 
> > > `lat`
> > > 
> > > > The latitude of this posting, in decimal degrees.
> > > 
> > > `long`
> > > 
> > > > The longitude of this posting, in decimal degrees.
> > > 
> > > `accuracy`
> > > 
> > > > An integer indicating the accuracy of the supplied lat/long value.
> > > 
> > > `bounds`
> > > 
> > > > An array defining the bounding box which completely encloses the
> > > > feature identified by the supplied lat/long value.  The array should
> > > > have 4 entries:
> > > > 
> > > > >     (min_lat, max_lat, min_long, max_long)
> > > 
> > > `country`
> > > 
> > > > The 3taps country code for this posting.
> > > 
> > > `state`
> > > 
> > > > The 3taps state code for this posting.
> > > 
> > > `metro`
> > > 
> > > > The 3taps metro area code for this posting.
> > > 
> > > `region`
> > > 
> > > > The 3taps region code for this posting.
> > > 
> > > `county`
> > > 
> > > > The 3taps county code for this posting.
> > > 
> > > `city`
> > > 
> > > > The 3taps city code for this posting.
> > > 
> > > `locality`
> > > 
> > > > The 3taps locality code for this posting.
> > > 
> > > `zipcode`
> > > 
> > > > The 3taps ZIP code for this posting.
> > 
> > __Note:__ If a posting comes in with only `lat` and `long` values, and
> > optionally either an `accuracy` or a `bounds` value, the 3taps Posting API
> > will ask the geolocator to calculate the exact location for the posting,
> > automatically filling in the `country`, `state`, `metro`, `region`, `city`,
> > `locality` and `zipcode` fields as appropriate.
> 
> `external_id` _(required)_
> 
> > A string or number that uniquely identifies the posting in the source
> > system.
> 
> `external_url`
> 
> > A URL pointing to the original posting.
> 
> `heading` _(required)_
> 
> > A string containing the heading for this posting.
> 
> `body`
> 
> > A string containing the body of this posting, in plain (unformatted) text.
> 
> `html`
> 
> > The original HTML text for this posting, encoded using base64 character
> > encoding to avoid problems with JSON representation of HTML text.
> 
> `timestamp` _(required)_
> 
> > The date and time at which the posting was created, as an integer number of
> > seconds since the 1st of January 1970 ("unix time"), in UTC.
> 
> `expires`
> 
> > The date and time at which this posting should expire, as an integer number
> > of seconds since the 1st of January 1970 ("unix time"), in UTC.
> 
> > __Note:__ If a posting comes in without an `expires` value, an appropriate
> > value will be calculated to expire the posting in seven days from when it
> > is added to the database.
> 
> `language`
> 
> > The 2-character ISO 639-1 language code indicating which language the
> > posting is in.
> 
> `price`
> 
> > The price associated with this posting, if any.  Note that this can be an
> > integer or a floating-point value, as desired.
> 
> `currency`
> 
> > The 3-character ISO-4217 currency code indicating which currency the price
> > is in.
> 
> `images`
> 
> > An array of image objects representing the images associated with this
> > posting.  Each image object can have the following fields:
> > 
> > > `full`
> > > 
> > > > The URL pointing to the full-sized image for this posting.
> > > 
> > > `full_width`
> > > 
> > > > The width of the full-sized image, in pixels.
> > > 
> > > `full_height`
> > > 
> > > > The height of the full-sized image, in pixels.
> > > 
> > > `thumbnail`
> > > 
> > > > The URL pointing to a thumbnail-sized image for this posting.
> > > 
> > > `thumbnail_width`
> > > 
> > > > The width of the thumbnail-sized image, in pixels.
> > > 
> > > `thumbnail_height`
> > > 
> > > > The height of the thumbnail-sized image, in pixels.
> 
> `annotations`
> 
> > A object holding the various annotations to associate with this posting.
> > Each field in this object maps the annotation name to its associated value,
> > which should always be a string.
> 
> `status`
> 
> > An object representing the posting's status.  The following fields are
> > currently supported:
> > 
> > > `offered`
> > > 
> > > > Set to __true__ if the posting is offered, __false__ otherwise.
> > > 
> > > `wanted`
> > > 
> > > > Set to __true__ if the posting is wanted, __false__ otherwise.
> > > 
> > > `lost`
> > > 
> > > > Set to __true__ if the posting is lost, __false__ otherwise.
> > > 
> > > `stolen`
> > > 
> > > > Set to __true__ if the posting is stolen, __false__ otherwise.
> > > 
> > > `found`
> > > 
> > > > Set to __true__ if the posting is found, __false__ otherwise.
> > > 
> > > `deleted`
> > > 
> > > > Set to __true__ if the posting has been deleted, __false__ otherwise.
> 
> > __Note:__ If a posting comes in without a `status` value, the posting's
> > status will be set to "offered".
> 
> `immortal`
> 
> > Set this to __true__ if the posting is to be immortal (ie, never expire).

Note that any field not marked as _required_ is optional.


### Caller Authentication ###

The current version of the Posting API does not require authentication, though
future versions will require callers to supply a valid authentication token.


### Using the Posting API ###

To add or update postings in the database, you should make an HTTP `POST`
request to the main URL for the Posting API, as described above.  The request
should have a Content-Type of `application/json`, and the body of the request
should be a JSON-encoded object with any combination of the following fields:

> `auth_token`
> 
> > This will eventually be the authentication token used to authenticate the
> > caller.  Note that this is currently ignored.
> 
> `posting`
> 
> > A single posting object to add or update.

> `postings`
> 
> > An array of posting objects to add or update.

Note that you can supply either a single posting, or an array of postings; the
Posting API will automatically handle both cases.

> > __Note:__ The Posting API can accept a maximum of 1,000 postings in a
> > single request.  If you have more than 1,000 postings to send, you will
> > need to split them up and send them through in chunks of no more than 1,000
> > postings at a time.

Each posting supplied to the Posting API should be a Posting Object, as
described above.

If the combination of the `source` value and the `source_id` value does not
already exist in the database, a new posting will be created.  Otherwise, the
existing posting with that `source` and `source_id` value will be updated.
When updating a posting, the supplied values are added to the existing posting.
If a field already has a value in the database, that value will be overwritten
by the new value.

Note that to delete a posting, you should update the posting to include a
status of `deleted`.

As each posting is processed, the Posting API calculates an __error response__
for the posting.  The error response will either be a string describing why the
posting could not be processed, or the value `null` which indicates that the
posting was processed succesfully.

Upon completion, the Posting API will send back a response with a Content-Type
of `application/json`, and the body of the response will be a JSON-formatted
object with the following fields:

> `error_responses`
> 
> > An array containing the error response for each posting.  The error
> > responses will be in the same order as the original postings, so the index
> > into the original postings can be used to find the error response for a
> > given posting.
> 
> `wait_for`
> 
> > An integer value telling the caller how long to wait before sending in
> > another batch of postings.  This is used to regulate the speed at which
> > postings are sent in, so that the Posting API doesn't get overloaded.


### Performance, Instrumentation and Reliability ###

The Posting API will make use of the __3taps Monitor__ to ensure that it can
meet the performance, instrumentation and reliability requirements discussed
below.

The Posting API must meet the following __performance__ requirements:

 * The HTTP `POST` call must always return within 100 miliseconds, regardless
   of the number of postings which were supplied.

 * Incoming postings can be queued, but must appear in search results and
   outgoing notification streams no later than 120 seconds after they are
   received by the Posting API.

The Posting API must support __instrumentation__ by recording the following
information on a minute-by-minute basis:

 * The number of postings received.

 * How long the API took to process these postings.

 * How much lag there was -- that is, the maximum amount of time that elapsed
   between receiving a posting and it being made available in search results
   and outgoing notification streams.

The Posting API must ensure ongoing __reliability__ by sending out an alert
(eg, an SMS text message) if any part of the Posting API becomes unresponsive
for more than 60 seconds, or if any of the above performance requirements are
no longer being met.


<center>
    <h1>
        The 3taps Data Commons
    </h1>
    <h3>
        System Administration Guide
    </h3>
    <h4>
        Version 0.1
    </h4>
</center>

The 3taps Data Commons system has been implemented as a Django application
built on top of a Postgres database.  It is intended to be run within the
Heroku server environment.

This document provides various pieces of important information needed to run
and administer the Data Commons system.


### System Settings ###

The Data Commons system makes use of various settings which can be changed to
customise the way the system operates.  How these settings are defined will
vary depending on whether you are running a development copy of the system, or
have deployed the system to Heroku:

 1. If you are running on a standalone development machine, the Data Commons
    system will look for a Python module named `custom_settings.py` within the
    main `dataCommons` directory (at the same level as the `settings.py`
    module).  If this module exists, the various settings can be customised by
    listing them as top-level variables within this module, for example:

>      DEBUG = True

 2. When you deploy the system to Heroku, the configuration settings must be
    defined using environment variables.  See the [Heroku
    docs](https://devcenter.heroku.com/articles/config-vars) for more
    information on setting up these environment variables.  In this case, the
    environment variable names must be prefixed by the string `DC_`, like this:

>      $ heroku config:add DC_DEBUG=True

>   The `DC_` prefix avoids possible issues where the name of a system setting
>   conflicts with an environment variable with the same name.

The following system settings are currently used by the 3taps Data Commons
system:

> __DEBUG__
> 
> > Set this to True to run the system in debugging mode.  Note that this must
> > be turned off on the production system.  Default value: `True`.
> 
> __TIME_ZONE__
> 
> > The name of the time zone to use.  See the Django docs for more information
> > on this setting.  Default value: `UTC`.
> 
> __SERVE_STATIC_MEDIA__
> 
> > Set this to True to serve static media files from within the development
> > server itself.  Default value: `False`.
> 
> __DATABASE_URL__
> 
> > A URL that holds the database location and authentication details.  When
> > running the system on Heroku, this value is provided automatically by the
> > server itself.  When running locally, you should define this setting to
> > a string with the following format:
> > 
> > >     engine://username:password@host:port/database_name
> > 
> > Or, for a database on the local machine, use:
> > 
> > >     engine://username:password@localhost/database_name
> > 
> > Where:
> > 
> > > __engine__ is the type of database engine being used (`postgres`,
> > > `mysql`, etc).
> > > 
> > > __username__ is the username to use when connecting to the database
> > > server.
> > > 
> > > __password__ is the password to use when connecting to the database
> > > server.
> > > 
> > > __host__ is the name or IP address of the database server's host machine.
> > > 
> > > __port__ is the TCP/IP port to use to connect to the database server.
> > > 
> > > __database_name__ is the name of the database to connect to
> > 
> > Note that the default value of this setting is `None`.
> 
> __LOG_DIR__
> 
> > The directory path to use for storing the various log files.  This defaults
> > to a `logs` directory at the top level of the data commons system.
> > 
> > __NOTE:__ You can only log to a file in the development version of the
> > system.  When deployed to Heroku, all internal logging to files must be
> > disabled so that the logs can be written to Heroku's internal console.
> 
> __ENABLE_DEBUG_LOGGING__
> 
> > Should debugging statements be written to the log?  Default value: `False`.
> 
> __ENABLE_QUERY_LOGGING__
> 
> > Should database queries be written to the log?  Default value: `False`.
> > Note that this should be turned off on the production server, as it can be
> > a performance bottleneck.
> 
> __LOGGING_DESTINATION__
> 
> > A string indicating where the debug or query log messages should be written
> > to.  Two values are currently supported:
> > 
> > > __file__
> > > 
> > > > Write the log messages to an appropriate log file in the specified log
> > > > directory.
> > > 
> > > __console__
> > > 
> > > > Write log messages to the system console.
> > 
> > This setting defaults to `file`, writing the log messages to a file.  Note
> > that this must be set to `console` on the production server.
> 
> __AWS_ACCESS_KEY_ID__   
> __AWS_SECRET_ACCESS_KEY__   
> __AWS_STORAGE_BUCKET_NAME__   
> __AWS_S3_SECURE_URLS__
> 
> > These settings configure access to the Amazon S3 server used to store the
> > static assets used by the Data Commons system.  Note that, at present,
> > these are used only to store the contents of the
> > `dataCommons/shared_static` directory on a server which the deployed
> > system can access.  Note that these settings default to `None`, meaning
> > that no Amazon S3 server will be used for storing the static assets.
> 
> __REDIS_HOST__
> 
> > The name of the host for the Redis instance used by this system.  This
> > defaults to None.
> 
> __REDIS_PORT__
> 
> > The TCP/IP port number to use to access the Redis instance.  This defaults
> > to None.
> 
> __REDIS_PASSWORD__
> 
> > The password to use to access the Redis instance.  This defaults to None.
> 
> __QUERY_TIMEOUT__
> 
> > The maximum time, in milliseconds, that a search or summary API call can
> > take.  If the request takes longer than this amount of time, an error will
> > be returned.  This defaults to 20,000 (ie, 20 seconds).

Note that more system settings will be added as they are required.


### Database Migration ###

The Data Commons system depends on the "south" database migration toolkit.  To
upgrade the database on the server to a new version, use the following command:

>     heroku run python ./manage.py migrate <APP_NAME>

where `<APP_NAME>` is the name of the application to migrate.  At present, the
following applications include database migrations:

 * `dataCommons.shared`   
 * `dataCommons.monitoringAPI`   

NOTE: The `dataCommons.shared` application defines all the core data structures
used by the Data Commons system.  While most of the database migrations are
automatically created, there is a hand-written migration named
`0002_text_indexes` that manually adds the appropriate tsvector fields and
indexes to the database.  This migration is specific to Postgres.


### Management Commands ###

The following management commands are supported by the Data Commons system:

> __clear_events__
> 
> > This management command, implemented by the `dataCommons.monitoringAPI`
> > application, flushes the internal event log used to record incoming events.
> 
> __clear_postings__
> 
> > This management command, implemented by the `dataCommons.shared`
> > application, deletes all existing postings from the database.  __USE THIS
> > COMMAND WITH CAUTION__.
> 
> __flush_cache__
> 
> > This management command, also implemented as part of the
> > `dataCommons.shared` application, flushes in the internal Redis cache used
> > by the Posting API to cache data sources, categories, category groups and
> > locations.  This is useful for flushing the cache when this information
> > changes.
> 
> __load_fixtures__
> 
> > This management command, implemented within the `dataCommons.shared`
> > application, loads the master list of data sources, categories, category
> > groups and locations into the database from the various fixture files
> > stored in `dataCommons/shared/fixtures` directory.
> 
> __flush_posting_queue__
> 
> > This management command, implemented by the `dataCommons.postingAPI`
> > application, flushes the internal queue of unprocessed postings.
> > 
> > > __WARNING:__ Using this command will obviously cause postings to be lost.
> > > It is intended for use only when problems occur with the system.

Note that these management commands can be run on the server by typing:

>     heroku run python ./manage.py <COMMAND_NAME>

where `<COMMAND_NAME>` is the name of the management command you want to run.


### Static Assets ###

When deployed to Heroku, the Data Commons system loads the various static
assets (from the `dataCommons/shared_static` directory) from an Amazon S3
instance.  The various __AWS\_*__ configuration settings define how to access
this instance.

Whenever you change the contents of the `dataCommons/shared_static` directory,
you need to re-upload the static assets to the server.  To do this, use the
following command:

>      python ./manage.py collectstatic


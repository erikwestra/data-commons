<center>
    <h1>
        The 3taps Data Commons
    </h1>
    <h3>
        Development Overview
    </h3>
    <h4>
        Version 0.1
    </h4>
</center>

This document describes how to work with the Data Commons source code, how to
deploy to Heroku and make changes to the system itself.


### Pre-Requisites ###

In order to work on the Data Commons system, you will need:

 1. An account with Heroku, which has been set up as a collaborator for the
    Data Commons Heroku project.

 2. An account with Github, which has been given permission to access the 3taps
    Github repositories.

 3. The Heroku toolbelt installed on your computer.

 4. The tools needed to run and deploy Python programs on Heroku.  Heroku's
    page on Python development has a nice list of
    [pre-requisites][heroku-python] telling you what you need to do.

  [heroku-python]: https://devcenter.heroku.com/articles/python#prerequisites


### Running the Data Commons System on a Development Machine ###

There are five steps to setting up a machine to work with the Data Commons
source code:

 1. Downloading the source and its dependencies into a "virtual environment".

 2. Setting up your local postgres database.

 3. Setting up a local Redis server.

 4. Setting local config vars.

 5. Initialising the database.

Let's look at each of these steps in turn.


#### 1. Downloading the Source and Dependencies into a Virtual Environment ###

Python applications written for Heroku make use of the "virtualenv" system for
keeping track of dependencies.  Setting up a virtual environment correctly can
be a little tricky -- the following instructions will get you there.

Firstly, start by creating a directory to hold your local copy of the system,
`cd` into that directory, and type the following to check out your local copy
of the Data Commons source code:

>     git clone git@github.com:3taps/3taps-data-commons.git .

You next need to set up the virtual environment in which your local copy of
the system will run.  To do this, type:

>     virtualenv venv --distribute

This creates a sub-directory named `venv` which holds the various virtual
environment files.  Before doing anything more, you need to activate the
virtual environment so that any further changes you make take place within that
environment.  To do this, type:

>     source venv/bin/activate

Notice that your command prompt changes to have a `(venv)` at the front -- this
tells you that you're running the virtual environment.  Any time you want to
run the program, or add/remove dependencies, you will need to activate the
virtual environment first.

With `(venv)` showing in the command prompt, you now want to download and
install the various dependencies used by the system.  To do this, type:

>     pip install -r requirements.txt

This will take a while as it downloads and installs all the dependencies needed
by the Data Commons system.


#### 2. Setting up the Local Postgres Database ####

You next need to set up a Postgres database for the system to use.  Typically,
you would use the `createdb` program to create a database for the Data Commons
system to use.  I called my local database "datacommons", though you can use
whatever name you like.

Make sure you record:

 * The name of the database.

 * If the database is hosted on a different computer, the IP address and
   TCP/IP port number needed to connect to the database server, 

 * The username and password needed to connect to the database.


#### 3. Setting up a Local Redis Server ####

The Data Commons system needs a Redis server to store cached data.  Set up a
suitable Redis server, and write down the following:

 * The name and TCP/IP port number of the host running the server.  This will
   be "localhost" and 6379 if you have configured a default installation of
   Redis on your machine.

 * The password needed to access the Redis server, if any.


#### 4. Setting Local Configuration Variables ####

When you check out the Data Commons source code, the top-level directory will
have a sub-directory named `dataCommons`.  This is where all the source code to
the Data Commons system can be found.  Inside that directory is a `settings.py`
module that defines the various settings used by the Data Commons system.
Because the `settings.py` module is part of the source code, we use a separate
module, named `custom_settings.py` to hold the machine-specific settings needed
by the Data Commons system.

In the `dataCommons` directory (ie, at the same level as `settings.py`), create
a new Python module named `custom_settings.py`.  Place the following into this
module:

>     DEBUG                   = True
>     TIME_ZONE               = 'America/Los_Angeles'
>     SERVE_STATIC_MEDIA      = True
>     DATABASE_URL            = "postgres://PG_USER:PG_PASS@PG_HOST/DB_NAME"
>     ENABLE_DEBUG_LOGGING    = True
>     ENABLE_QUERY_LOGGING    = True
>     LOGGING_DESTINATION     = "file"
>     AWS_ACCESS_KEY_ID       = "AKIAJ5TQE7OVFO67QFXA"
>     AWS_SECRET_ACCESS_KEY   = "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"
>     AWS_STORAGE_BUCKET_NAME = "datacommons.3taps.com"
>     AWS_S3_SECURE_URLS      = False
>     REDIS_HOST              = "REDIS_HOST"
>     REDIS_PORT              = REDIS_PORT
>     REDIS_PASSWORD          = "REDIS_PASS"
>     QUERY_TIMEOUT           = 2000

Make sure you supply your own values for:

> `PG_USER`
> 
> > The username to use to access the Postgres database.
> 
> `PG_PASS`
> 
> > The password to use to access the Postgres database.
> 
> `DB_NAME`
> 
> > The name of the Postgres database to use.
> 
> `REDIS_HOST`
> 
> > The name of the machine hosting the Redis server.
> 
> `REDIS_PORT`
> 
> > The TCP/IP port to use to access the Redis server.
> 
> `REDIS_PASSWORD`
> 
> > The password to use to access the Redis server.  Set this to `None`
> > (without quotes) if your server does not require a password.

__NOTE:__ While these settings are stored in a `custom_settings.py` module on
your local development machine, they are defined in a completely different way
on the production server.  See the section on useful Heroku commands, below,
for more information.


#### 5. Initialising the Database ####

Once the system has been installed and configured, you next need to set up the
database, apply the database migrations, and install the "fixtures" used to
supply initial data used by the system.  Let's look at these steps one at a
time.

Firstly, type the following into the command prompt:

>     python manage.py syncdb

This will do the initial database setup.  You'll be asked to create an "admin"
user, just give it a username and password you can remember -- we're not using
admin users yet, but it's worth having one in case we do this down the track.

Once this has finished, you next need to apply the database migrations.  You
have to do this for each application within the Data Commons system that use
database migrations -- both applications within the Data Commons system itself,
and in the libraries it makes use of.  Here are the necessary commands:

>      python manage.py migrate kombu.transport.django   
>      python manage.py migrate djcelery   
>      python manage.py migrate dataCommons.shared   
>      python manage.py migrate dataCommons.monitoringAPI   

Finally, you'll need to setup the master lists of categories, data sources and
locations used by the system.  These are currently stored as database
"fixtures", so you'll need to run the following command to load this data into
the database:

>     python manage.py load_fixtures

Once this has all been done, you should have your own local copy of the system,
and be able to run it.  To start the system, make sure that `(venv)` is showing
in your command prompt, and type:

>     foreman start

This will start up the application using the "foreman" process manager.  Both
the web dyno and the worker dyno will be up and running on your computer.

You should be able to access the admin interface at:

>     http://127.0.0.1:5000/admin

Similarly, you can make various API calls like this:

>     http://127.0.0.1:5000/api/latest/search?text=bike


### Making Changes to the Source ###

Because the source code to the Data Commons system is stored on Github, you can
make changes on any computer which has the system installed.  As you make
changes, commit them to the Github repository in the usual way, eg:

>     git commit -a -m 'Implemented "Lost Widget" report.'
>     git push

Just like with any other system, you can use Github's commands to merge changes
made by various people, create new branches of the source code, etc.


### Database Migrations ###

The Data Commons system makes use of Django South to keep track of changes made
to the database.  While we occasionally have to make a postgres-specific
database migration (eg, to add full-text indexing), generally you create the
database migration module by typing:

>     python manage.py schemamigration dataCommons.shared --auto auto

This creates a new migration file (in `dataCommons.shared.migrations`) that
automatically updates the database to match the current schema (defined in
`dataCommons.shared.models`).  You then apply this database migration using:

>     python manage.py migrate dataCommons.shared

Note that you will have to add the newly-created database migration file into
the Github repository.


### Deploying to Heroku ###

When you are ready to deploy the system to Heroku, you use `git` to push your
changes to the Heroku server.  Before you can do this, you need to set up
Heroku as a remote repository, by typing the following:

>     git remote add heroku git@github.com:3taps/3taps-data-commons.git

You can then commit your changes to Heroku by typing:

>     git push heroku

When you push changes to Heroku, the server automatically shuts down the
running system, commits your latest version of the source into Heroku's own
private repository, and then restarts the system.  Note that it does __not__
apply you database migrations for you.  To do that, type the following command
once the new version has been deployed:

>     heroku run python manage.py migrate dataCommons.shared


### Useful Heroku Commands ###

Heroku includes a number of useful commands which you can use to manage the
system.  These include:

>     heroku run python manage.py shell
> 
> > Start up a Python shell within the Data Commons system.  You can then do
> > things like:
> > 
> > >     from dataCommons.shared.models import *
> > >     for posting in Posting.objects.filter(status_stolen=True):
> > >         print posting.source.source, posting.external_id
> 
>     heroku logs
> 
> > Display the most recent entries in the Heroku logs file.  While we use the
> > `Logentries` add-on to provide a web interface to the Heroku logs,
> > accessing the log directly can be useful at times.
> 
>     heroku logs -t
> 
> > Display the Heroku log, and keep it updated as new entries come in.
> 
>     heroku ps
> 
> > List the processes running on the server.
> 
>     heroku ps:scale web=1
> 
> > Change the number of dynos running the "web" worker.  Note that there are
> > two workers in the system: "web" for the web interface, and "worker" for
> > running the background posting processor.
> 
>     heroku restart
> 
> > This restarts the application on Heroku.  I usually use `heroku ps:scale`
> > instead to shut down and then restart the application.
> 
>     heroku pg:psql
> 
> > This launches the command-line client to the Postgres database.
> 
>     heroku maintenance:on   
>     heroku maintenance:off
> 
> > Turn on or off maintenance mode for the application.  Maintenance mode
> > disables all HTTP access to the system, while allowing internal processes
> > to keep running.  This can be useful when updating the system or doing
> > lengthy database schema changes.
> 
>     heroku config
> 
> > List the various config variables which are used by Heroku.  Note that on
> > the production server, config settings are used instead of the
> > `custom_settings.py` module.  For each custom setting, a config variable is
> > set up with the name of the custom setting, prepended with the characters
> > `DC_`.  So, for example, the `REDIS_HOST` setting is defined by a config
> > variable named `DC_REDIS_HOST`.
> 
>     heroku config:add AAA=BBB CCC=DDD ...
> 
> > Change the value of one or more config variables.  Note that this has the
> > effect of restarting the server, as the config variables can affect how the
> > server operates.

Finally, note that if you want to access these commands, you need your current
directory set to the main directory into which which you checked out the data
commons source code.  If you aren't in this directory, you will need to specify
which application you want the command to apply to.  For example:

>     heroku logs --app data-commons

### The Heroku Web Interface ###

If you go to the main Heroku web site and log in, you will be able to see the
Data Commons system listed as one of your applications in the Heroku dashboard.
In the __Resources__ tab, you can see the various add-ons which we are using to
keep track of the system:

> __Heroku Postgres Crane__
> 
> > This is the Postgres database we are using.  Clicking on this entry shows
> > you various settings for the database, including the URL used to access it,
> > how big the database is, which version of Postgres it is running, etc.
> 
> __Logentries__
> 
> > This is a simple logging system which lets us (for free) view the Heroku
> > logs in a web interface.  It allows us to tag log entries, and to filter
> > the log entries based on timeframe and either a search string or a regular
> > expression.
> 
> __MyRedis__
> 
> > This is a free Redis host, used for caching.
> 
> __New Relic__
> 
> > This is the interface to the New Relic application monitoring system.
> > Click on it to see the fancy New Relic interface -- there are a ton of
> > useful graphs and other reports, as well as options for monitoring the
> > background tasks, application profiling, etc.  I haven't even started to
> > see all that New Relic can do for us, and I'm sure it'll be incredibly
> > useful for us to see what's happening behind-the-scenes.
> 
> __PG Backups Plus__
> 
> > This is Heroku's add-on for making backups of the Postgres database, and
> > for migrating the database between Heroku plans.


### Data Commons Internal Tools ###

Within the Data Commons system itself, there are a number of useful tools which
you can use to monitor the performance of the system.  Firstly, the following
URL will give you access to the "admin" interface:

>      http://data-commons.herokuapp.com/admin

From there, you can generate various reports showing you how the system is
working:

> __Posting Queue Size__
> 
> > This report shows you how many postings are queued up waiting to be
> > processed and inserted into the database.  Note that this report relies on
> > `POSTINGS_QUEUED` and `POSTINGS_DEQUEUED` events being recorded correctly
> > by the Monitoring API.  These events can occasionally get out of sync,
> > leading to the report claiming that there are postings to be processed
> > when there aren't -- this appears to be due to a bug which I haven't been
> > able to chase down yet.
> 
> __Posting Summary__
> 
> > This report shows the number of postings added to the database.  Note that
> > this report currently relies on summing up the number of postings in the
> > database, which takes a long time, so it's best to run this report over a
> > few small timeframes (eg, every hour for the past five hours), or each day
> > for the past day), rather than trying to count up the total number of
> > postings over many days.  If you try doing this, the report may time out
> > when it hits Heroku's 30-second response time limit.
> 
> __Processing Times__
> 
> > This report shows how long it's taking the Posting API to process the
> > queued postings.  This is quite an interesting view of the performance of
> > the system.
> 
> __Search Request Times__
> 
> > This report shows how long it took to process each successful search
> > request.  Note that it doesn't include any requests which took more than 30
> > seconds to complete, as these time out.
> 
> __Summary Request Times__
> 
> > This report shows how long it took to process each successful summary
> > request.  Once again, it doesn't include timed-out summary requests.
> 
> __Timed Out Queries__
> 
> > This report provides a log of the SQL queries that took too long to
> > complete.  Rather than a chart, this report consists of a simple table
> > listing each SQL query and when it was executed.

As well as these reports, you can use a secret feature of the Search API to see
how it is converting search requests into SQL queries: if you include
`return_sql=1` in your search parameters, the API will return the raw SQL
statement used to run the query, in plain text.  For example:

>     http://data-commons.herokuapp.com/api/latest/search?text=bike&return_sql=1

will return the following:

>     SELECT "shared_posting"."id", "shared_posting"."account_id",
>     "shared_posting"."source_id", "shared_posting"."category_id",
>     "shared_posting"."category_group_id", "shared_posting"."location_latitude",
>     "shared_posting"."location_longitude", "shared_posting"."location_accuracy",
>     "shared_posting"."location_country_id", "shared_posting"."location_state_id",
>     "shared_posting"."location_metro_id", "shared_posting"."location_region_id",
>     "shared_posting"."location_county_id", "shared_posting"."location_city_id",
>     "shared_posting"."location_locality_id", "shared_posting"."location_zipcode_id",
>     "shared_posting"."external_id", "shared_posting"."external_url",
>     "shared_posting"."heading", "shared_posting"."body",
>     "shared_posting"."html", "shared_posting"."timestamp",
>     "shared_posting"."inserted", "shared_posting"."expires",
>     "shared_posting"."language", "shared_posting"."price",
>     "shared_posting"."currency", "shared_posting"."status_offered",
>     "shared_posting"."status_lost", "shared_posting"."status_stolen",
>     "shared_posting"."status_found", "shared_posting"."status_deleted",
>     "shared_posting"."has_image", "shared_posting"."immortal" FROM
>     "shared_posting" WHERE ((heading_tsv @@ plainto_tsquery(bike)) OR
>     (body_tsv @@ plainto_tsquery(bike)) AND "shared_posting"."status_deleted"
>     = False ) ORDER BY "shared_posting"."id" DESC LIMIT 10

This SQL statement can then be passed to the `psql` command-line client, where
you can analze the query and see what needs to be done to improve performance.

Note that when you use the `return_sql=1` parameter, the query itself will not
be executed.

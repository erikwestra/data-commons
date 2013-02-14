""" urls.py

    This module defines the top level URLs used by the dataCommons system.

    Note that API versioning is not supported yet -- we simply hardwire the
    version numbers into the URLs.
"""
from django.conf.urls import *

#############################################################################

urlpatterns = []

# The posting API:

urlpatterns += patterns('',
    ('^api/v1/posting/',     include("dataCommons.postingAPI.urls")),
    ('^api/latest/posting/', include("dataCommons.postingAPI.urls")),
)

# The search API:

urlpatterns += patterns('',
    ('^api/v1/search/',     include("dataCommons.searchAPI.urls")),
    ('^api/latest/search/', include("dataCommons.searchAPI.urls")),
)

# The summarizer API:

urlpatterns += patterns('',
    ('^api/v1/summarizer/',     include("dataCommons.summarizerAPI.urls")),
    ('^api/latest/summarizer/', include("dataCommons.summarizerAPI.urls")),
)

# The monitoring API:

urlpatterns += patterns('',
    ('^api/v1/monitoring/',     include("dataCommons.monitoringAPI.urls")),
    ('^api/latest/monitoring/', include("dataCommons.monitoringAPI.urls")),
)

# The reporting application:

urlpatterns += patterns('',
    ('^reporting/', include("dataCommons.reporting.urls")),
)

# The admin interface:

urlpatterns += patterns('',
    ('^admin/', include("dataCommons.admin.urls")),
)

# The polling API:

urlpatterns += patterns('',
    ('^api/v1/poll/',     include("dataCommons.pollingAPI.urls")),
    ('^api/latest/poll/', include("dataCommons.pollingAPI.urls")),
)



""" dataCommons.shared.lib.dataCache

    This module implements a generic mechanism for caching data.  It uses Redis
    behind-the-scenes to cache any arbitrary data structure, and allows for
    cache entries to be flushed upon request.

    Note that this module requires a REDIS_CONFIG setting which has the
    following entries:

        host

            The name or IP address of the server running the Redis host.

        port

            The TCP/IP port to use to access the Redis host.
"""
import cPickle as pickle

from django.conf import settings

import redis

#############################################################################

# The following string is used as a prefix for our keys in the redis server.
# This ensures that we don't use the same key as some other client using the
# same server.

PREFIX = "3taps.dataCommons.dataCache."

#############################################################################

def set(key, value):
    """ Set the given cache entry to the given value.

        'key' must be a string, and 'value' can be any Python data structure,
        including the value None.

        We associate the given value with the given key in our data cache.
    """
    cache = _get_cache()

    if value == None:
        cache.delete(PREFIX + key)
    else:
        cache.set(PREFIX + key, pickle.dumps(value))

#############################################################################

def get(key):
    """ Retrieve the value currently associated with the given key.

        If there is no value associated with that key, we return None.
    """
    cache = _get_cache()

    pickled_value = cache.get(PREFIX + key)
    if pickled_value == None:
        return None
    else:
        return pickle.loads(pickled_value)

#############################################################################

def delete(key):
    """ Delete the given entry from our data cache.
    """
    cache = _get_cache()
    cache.delete(PREFIX + key)

#############################################################################

def flush():
    """ Remove all entries from our data cache.
    """
    cache = _get_cache()
    keys = []
    for key_name in cache.keys(PREFIX + "*"):
        keys.append(key_name)
    cache.delete(*keys)

#############################################################################
#                                                                           #
#                    P R I V A T E   D E F I N I T I O N S                  #
#                                                                           #
#############################################################################

def _get_cache():
    """ Return the redis.Redis object to use for accessing the Redis cache.

        Note that we use a private global variable so that only one instance of
        the redis cache object will be used per thread.
    """
    global _redis_cache

    try:
        return _redis_cache
    except NameError:
        _redis_cache = redis.Redis(**settings.REDIS_CONFIG)
        return _redis_cache


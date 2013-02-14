""" dataCommons.shared.lib.settingsImporter

    This module makes it easier to work with settings in a Django application
    that has to run in both a Heroku-style environment (for production) and on
    a local machine (for development).

    Rationale
    ---------

    For various philosophical and technical reasons, Heroku doesn't support
    local configuration files, and an application's settings must be defined
    using environment variables.  See the following URLs for more information:

        https://devcenter.heroku.com/articles/config-vars
        http://www.12factor.net/config

    Environment variables, however, are not a good way of defining settings
    while developing an application or running it locally.  When running
    locally, you have basically three options for defining your settings using
    environment variables:

      1. You can set each environment variable by hand every time the
         application is run, eg:

            $ SETTING_1=value SETTING_2=value python manage.py runserver

      2. You can store the environment variables in a file, and source that
         file for each terminal session where you want to run the application:

            $ source my_settings.txt

      3. You can add the environment variables to your ".bashrc" file so they
         are imported automatically every time you open a terminal session.

    Options #1 and #2 have the major disadvantage of adding steps to the
    development process, and leading to strange behaviour if you forget to do
    the step.  Option #3 places your application's settings in a non-intuitive
    place, and pollutes your environment for every terminal session, not just
    those where you are developing this particular application.  It also makes
    it very hard to develop different sets of applications, with different
    settings, on the same machine.


    The Importing Process
    ---------------------

    When importing a setting, the SettingsImporter will first look to see if
    there is an environment variable set for that setting.  If so, the setting
    will be taken from the environment variable.  Otherwise, it will look for
    an entry in the custom settings module, and if one is present that setting
    value will be used.  Finally, if neither an environment variable nor a
    custom setting is defined, the default value for that setting will be used
    instead.

    Note that the SettingsImporter will automatically convert an environment
    variable in the correct data type.  For example, if the default value for a
    setting is a boolean, it will convert the environment variable's value from
    a string to a boolean.  The same applies to integer and floating-point
    values.

    Here is an example of importing settings using the SettingsImporter:

        # settings.py

        from settingsImporter import SettingsImporter

        import_setting = SettingsImporter(settings_namespace=globals(),
                                          custom_settings="custom_settings",
                                          env_prefix="MY_APP_")

        ...

        import_setting("SETTING_1", default=True)
        import_setting("SETTING_2", default="myView")
        ...

    Each call to import_setting() loads the given setting, falling back to the
    given default value if no environment variable or custom setting is
    defined, and inserts that setting into the global namespace for the
    settings module.
"""
import os
import types

#############################################################################

class SettingsImporter:
    """ A class for simplifying the process of importing settings.
    """
    def __init__(self, settings_namespace=None,
                       custom_settings="custom_settings",
                       env_prefix=""):
        """ Standard initialiser.

            The parameters are as follows:

                'settings_namespace'

                    This should be set to globals() by the initialiser.  It
                    defines the namespace (dictionary) into which the settings
                    will be inserted.

                'custom_settings'

                    The name of the module to import the custom settings from.

                'env_prefix'

                    A string to use as a prefix for each environment variable
                    that is to be imported.  For example, if 'env_prefix' is
                    set to "MY_APP_", and we are importing a setting named
                    "BLAH", the importer will look for an environment variable
                    named "MY_APP_BLAH".
        """
        self._namespace       = settings_namespace
        self._custom_settings = self._import_module(custom_settings)
        self._env_prefix      = env_prefix


    def __call__(self, setting, default=None):
        """ Call the settings importer to import a single setting.

            The parameters are as follows:

                'setting'

                    The name of the setting to import.

                'default'

                    The default value to use for this setting if it can't be
                    imported.

            We look for an environment variable named 'env_prefix+setting', and
            use that value if it exists.  Otherwise, we look for a entry in the
            custom settings module (if it exists) with the name 'setting'.
            Finally, we fall back to using the given default value.

            Whatever value we use for the setting, that setting will be stored
            into the settings_namespace dictionary, using the given setting name
            and value.
        """
        env_var = self._env_prefix + setting
        if env_var in os.environ:
            value = self._coerce_to_type(os.environ[env_var], type(default))
        elif self._custom_settings != None and hasattr(self._custom_settings,
                                                       setting):
            value = getattr(self._custom_settings, setting)
        else:
            value = default

        self._namespace[setting] = value

    # =====================
    # == PRIVATE METHODS ==
    # =====================

    def _import_module(self, module_name):
        """ Import and return the given module.

            If the given module does not exist, we return None.
        """
        try:
            module = __import__(module_name)
        except ImportError:
            return None

        # Extract the module from a package, if necessary.  See the
        # documentation for the __import__() built-in function for more
        # information on this.

        components = module_name.split(".")
        for component in components[1:]:
            module = getattr(module, component)
        return module


    def _coerce_to_type(self, s, to_type):
        """ Coerce the given string value to the given type.

            If 'type' is NoneType, no type-conversion will be done.  Otherwise,
            we will attempt to convert the given string to the given type of
            data.

            Note that we raise a RuntimeError if the value cannot be coerced.
            For example, if to_type is IntType and s is "abc".
        """
        if to_type == types.NoneType:
            # No default value specified -> no type conversion is possible.
            return s
        elif to_type == types.BooleanType:
            if s.lower() in ["true", "t", "yes", "y", "1"]:
                return True
            elif s.lower() in ["false", "f", "no", "n", "0"]:
                return False
            else:
                raise RuntimeError("Invalid boolean: " + repr(s))
        elif to_type == types.IntType:
            try:
                return int(s)
            except ValueError:
                raise RuntimeError("Invalid int: " + repr(s))
        elif to_type == types.LongType:
            try:
                return long(s)
            except ValueError:
                raise RuntimeError("Invalid long: " + repr(s))
        elif to_type == types.FloatType:
            try:
                return float(s)
            except ValueError:
                raise RuntimeError("Invalid float: " + repr(s))
        elif to_type == types.StringType:
            try:
                return str(s)
            except ValueError:
                raise RuntimeError("Invalid string: " + repr(s))
        elif to_type == types.UnicodeType:
            try:
                return unicode(s)
            except ValueError:
                raise RuntimeError("Invalid unicode: " + repr(s))
        else:
                raise RuntimeError("Unsupported type: " + repr(to_type))


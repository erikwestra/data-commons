""" dataCommons.admin.views

    This module defines the various view functions for the admin application.
"""
from django.shortcuts import render_to_response
from django.template  import RequestContext

#############################################################################

def main(request):
    """ Respond to the "/admin" URL.

        We display the main "admin" page.  Note that there is no
        password-protection at the moment; we'll add that later.
    """
    options = [
                ("Generate Reports", "/reporting"),
              ]

    return render_to_response("admin/templates/main.html",
                              {'options' : options},
                              context_instance=RequestContext(request))


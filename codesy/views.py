import hashlib

from django.template import RequestContext
from django.shortcuts import render_to_response


# Create your views here.
def home(request):
    gravatar_url = ''
    if request.user.is_authenticated():
        gravatar_url = "http://www.gravatar.com/avatar/{}?s=40".format(
            hashlib.md5(request.user.email).hexdigest()
        )

    return render_to_response("home.html",
                              {'gravatar_url': gravatar_url},
                              RequestContext(request)
                             )

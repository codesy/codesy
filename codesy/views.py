import hashlib
import os

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from rest_framework.viewsets import ModelViewSet

from .base.models import User
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    """
    API endpoint for bids. Users can only list, create, retrieve, update, or delete their own bids.
    """
    model = User
    serializer_class = UserSerializer

    def get_object(self, qs=None):
        return self.request.user


def home(request):
    gravatar_url = ''
    if request.user.is_authenticated():
        gravatar_url = "http://www.gravatar.com/avatar/{}?s=40".format(
            hashlib.md5(request.user.email).hexdigest()
        )

    firstrun = "firstrun" in request.GET or False

    return render_to_response("home.html",
                              {'gravatar_url': gravatar_url,
                               'firstrun': firstrun},
                              RequestContext(request)
                             )


def revision(request):
    return HttpResponse(os.environ.get('COMMIT_HASH', ''),
                        content_type='text/plain')

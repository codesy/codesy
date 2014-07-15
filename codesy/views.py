import hashlib
import os

import braintree

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response


BRAINTREE_CONFIG = {
    'merchant_id': os.environ.get('BRAINTREE_MERCHANT_ID', ''),
    'public_key': os.environ.get('BRAINTREE_PUBLIC_KEY', ''),
    'private_key': os.environ.get('BRAINTREE_PRIVATE_KEY', '')
}
braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  **BRAINTREE_CONFIG)

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


def revision(request):
    return HttpResponse(os.environ.get('COMMIT_HASH', ''),
                        content_type='text/plain')


def client_token(request):
    if request.user.is_authenticated():
        client_token = braintree.ClientToken.generate({
            # "customer_id": request.user.id
        })
    return HttpResponse(client_token, content_type='text/plain')

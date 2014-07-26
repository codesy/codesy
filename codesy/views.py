import hashlib
import os

import braintree

from django.contrib import messages
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect


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

    firstrun = "firstrun" in request.GET or False

    return render_to_response("home.html",
                              {'gravatar_url': gravatar_url,
                               'firstrun': firstrun},
                              RequestContext(request)
                             )


def revision(request):
    return HttpResponse(os.environ.get('COMMIT_HASH', ''),
                        content_type='text/plain')


def braintree_token(request):
    if request.user.is_authenticated():
        braintree_token = braintree.ClientToken.generate({
            # "customer_id": request.user.id
        })
    return HttpResponse(braintree_token, content_type='text/plain')


def deposit(request, username):
    if request.method == "POST":
        amount = request.POST["amount"]
        nonce = request.POST["payment_method_nonce"]
        result = braintree.Transaction.sale({
            "amount": amount,
            "payment_method_nonce": nonce
        })
        if result.is_success:
            messages.success(request, "Deposited %s. Transaction ID: %s" %
                             (amount, result.transaction.id))
        else:
            messages.error(request, "Error: %s" % result.message)
        return redirect('home')

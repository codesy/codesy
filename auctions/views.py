from django.contrib.sites.shortcuts import get_current_site

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Bid
from .serializers import BidSerializer


class BidViewSet(ModelViewSet):
    """
    API endpoint for bids. Users can only list, create, retrieve, update, or
    delete their own bids.
    """
    model = Bid
    serializer_class = BidSerializer

    def pre_save(self, obj):
        # TODO: charge the user's credit card via balanced
        obj.user = self.request.user

    def get_queryset(self):
        qs = super(BidViewSet, self).get_queryset()
        return qs.filter(user=self.request.user)


class GetBid(APIView):
    """
    API endpoint for a single bid form.

    Requests for /bid/?url= will receive the HTML form for creating a bid (if
    none exists) or updating the user's existing bid.

    url -- url of an OSS issue or bug
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, format=None):
        # Pass current domain because the form is rendered on other domains
        current_site = get_current_site(request)
        url = self.request.QUERY_PARAMS.get('url')
        try:
            bid = Bid.objects.get(user=self.request.user, url=url)
        except Bid.DoesNotExist:
            bid = None
        resp = Response({'bid': bid,
                         'url': url,
                         'domain': current_site.domain},
                        template_name='bid.html')
        return resp

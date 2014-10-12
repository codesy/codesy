from rest_framework import serializers

from .models import Bid


class BidSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.Field(source='user')

    class Meta:
        model = Bid
        fields = ('id', 'user', 'url', 'ask', 'offer')
        read_only_fields = ('id',)


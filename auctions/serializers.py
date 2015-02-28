from rest_framework import serializers

from .models import Bid, Claim


class BidSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Bid
        fields = ('id', 'user', 'url', 'ask', 'offer')
        read_only_fields = ('id',)


class ClaimSerializer(serializers.HyperlinkedModelSerializer):
    claimant = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Claim
        fields = ('id', 'issue', 'claimant')
        read_only_fields = ('id',)

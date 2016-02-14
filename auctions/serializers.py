from rest_framework import serializers

from .models import Bid, Claim, Vote


class BidSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Bid
        fields = ('id', 'user', 'url', 'ask', 'offer')
        read_only_fields = ('id',)


class ClaimSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Claim
        fields = ('id', 'issue', 'user', 'evidence', 'status')
        read_only_fields = ('id',)


class VoteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Vote
        fields = ('id', 'user', 'claim', 'approved')
        read_only_fields = ('id',)

from rest_framework import serializers

from .models import Bid, Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.Field(source='user')

    class Meta:
        model = Profile
        fields = ('url', 'balanced_card_href', 'balanced_bank_account_href',)


class BidSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.Field(source='user')

    class Meta:
        model = Bid
        fields = ('id', 'user', 'url', 'ask', 'offer')
        read_only_fields = ('id',)


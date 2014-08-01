from rest_framework import serializers

from .models import Bid, Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'balanced_card_href', 'balanced_bank_account_href')
        read_only_fields = ('user',)
        write_only_fields = ('balanced_card_href',
                             'balanced_bank_account_href')


class BidSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bid
        fields = ('user', 'url', 'ask', 'offer')

    user = serializers.Field(source='user')

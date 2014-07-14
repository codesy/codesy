from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Bid


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'url')
        read_only_fields = ('username',)


class BidSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bid
        fields = ('user', 'url', 'ask', 'offer')

    user = serializers.Field(source='user')

from rest_framework import serializers

from .base.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'balanced_card_href',
                  'balanced_bank_account_href')
        read_only_fields = ('id', 'username')

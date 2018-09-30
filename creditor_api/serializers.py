from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Offer
from accounts.serializers import UserSerializer


class OfferSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Offer
        fields = '__all__'


class CreateOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        exclude = ('user',)

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise ValidationError("No 'request' in context")
        if not hasattr(request, 'user'):
            raise ValidationError("No 'user' in 'request'")
        if request.user.role == 'partner':
            raise ValidationError("Partner can't create offers")

        validated_data['user'] = request.user
        return Offer.objects.create(**validated_data)

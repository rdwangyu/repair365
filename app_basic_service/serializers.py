from rest_framework import serializers
from .models import *

class UserMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMasterModel
        fields = ['fullname', 'avatar', 'identity_card_0', 'identity_card_1',
                  'business_license', 'phone', 'address', 'work_year']

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('phone not digit')
        if len(value) != 11:
            raise serializers.ValidationError("phone too short")
        return value

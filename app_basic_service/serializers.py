from rest_framework import serializers
from .models import *

class UserMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMasterModel
        fields = '__all__'

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('phone not digit')
        if len(value) != 11:
            raise serializers.ValidationError("phone too short")
        return value

class UserCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustomerModel
        fields = '__all__'

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('phone not digit')
        if len(value) != 11:
            raise serializers.ValidationError("phone too short")
        return value


class RepairOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrderModel
        fields = '__all__'

    def validate_contact_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('phone not digit')
        if len(value) != 11:
            raise serializers.ValidationError("phone too short")
        return value


        


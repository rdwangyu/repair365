from rest_framework import serializers
from .models import RepairOrder, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['openid', 'name', 'phone', 'user_type']

class RepairOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairOrder
        fields = [
            'id',
            'receiver', 'sponsor',
            'description', 'phone',
            'address',
            'created_at', 'updated_at',
            'appointment_time', 'actual_arrival_time',
            'order_status',
            'amount', 'payment_method',
            'rating', 'comment'
        ]
        read_only_fields = ['sponsor']

from rest_framework import serializers
from .models import RepairForm

class RepairFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairForm
        fields = [
            'id', 'sponsor', 'receiver',
            'description',
            'address',
            'created_at', 'updated_at',
            'appointment_time', 'actual_arrival_time',
            'order_status',
            'amount', 'payment_method',
            'rating', 'comment'
        ]

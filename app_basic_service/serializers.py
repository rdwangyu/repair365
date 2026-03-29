from rest_framework import serializers
from .models import *

class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    image_type = serializers.CharField(required=False, max_length=50)
    
    def validate_image(self, value):
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("图片大小不能超过10MB")
        
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(f"只支持 {', '.join(allowed_types)} 格式")
        
        return value

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
    assignee = UserMasterSerializer(read_only=True)
    sponsor = UserCustomerSerializer(read_only=True)
    class Meta:
        model = RepairOrderModel
        fields = '__all__'

    def validate_contact_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('phone not digit')
        if len(value) != 11:
            raise serializers.ValidationError("phone too short")
        return value


        

